"""Harbor's dashboard backend. Maya's browser talks to this; this talks to the Status API.

Two ways to sign in, switched by the lab (`harbor lab sign-in password|harbor`):
  * section 03: a password form, checked here, then a session record in the shared store and a cookie;
  * section 08: "Sign in with Harbor", OpenID Connect with Harbor Sign-in, then the same kind of session, which now
    also keeps the ID, access and refresh tokens on the server.
Either way the browser holds only the session cookie. Two copies of this server run behind the gateway
(dashboard-a and dashboard-b); they share one session store, so either can serve Maya.
Lab code: one user, fictional values, plain HTTP on *.localhost names.
"""
import json
import os
import secrets
import time
from html import escape
from urllib.parse import urlencode

import httpx
import jwt
import valkey
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from common import AUTHORIZE, CERTS, DASHBOARD, ISSUER, LAB_ADMIN, STATUS_API, TOKEN, lab_note, new_pkce, page, short

SERVER = os.environ.get("HARBOR_SERVER", "dashboard")
CLIENT_ID = "harbor-dashboard"
CLIENT_SECRET = os.environ["DASHBOARD_CLIENT_SECRET"]
CALLBACK = f"{DASHBOARD}/auth/callback"
API_TOKEN = os.environ["DASHBOARD_API_TOKEN"]  # section 05: the opaque token prepared for the dashboard backend

app = FastAPI(title="Harbor dashboard")
store = valkey.Valkey(host=os.environ.get("VALKEY_HOST", "valkey"), port=6379, decode_responses=True)
hasher = PasswordHasher()
USERS = {"maya": {"name": "Maya", "password_hash": hasher.hash("demo-only")}}
NOBODY = hasher.hash("an unknown user takes as long to refuse as a wrong password")
ACCOUNTS = {"maya-01": "maya"}  # section 08: Harbor Sign-in's subject -> the dashboard's account
JWKS = jwt.PyJWKClient(CERTS)
# Every 401 names how to authenticate (RFC 9110, 15.5.2). No registered scheme describes a sign-in form and its cookie,
# so this one is Harbor's own, in the form of an expired draft's "Cookie" scheme (draft-broyer-http-cookie-auth).
CHALLENGE = 'Cookie realm="Harbor dashboard", form-action="/login", cookie-name="session"'


def lab(name: str, default: str) -> str:
    """The lab's switches live in the shared store, so both dashboard servers follow them."""
    return store.get(f"lab:{name}") or default


# ---- sessions (section 03): a record on the server, its ID in a cookie --------------------------------------------

def create_session(user: str, **extra) -> tuple[str, dict]:
    session_id = secrets.token_urlsafe(32)  # long and unpredictable
    while session_id.startswith("-"):  # lab only: so the ID can be pasted into a command without looking like an option
        session_id = secrets.token_urlsafe(32)
    lifetime = int(store.getdel("lab:session_ttl") or 1800)  # 30 minutes; the lab's short lifetime is for one sign-in
    now = time.time()
    record = {"user": user, "created": now, "expires": now + lifetime, "csrf_token": secrets.token_urlsafe(24),
              "created_by": SERVER, **extra}
    store.set(f"session:{session_id}", json.dumps(record), ex=lifetime)
    return session_id, record


def find_session(request: Request) -> tuple[str | None, dict | None]:
    session_id = request.cookies.get("session")
    if not session_id:
        return None, None
    raw = store.get(f"session:{session_id}")
    if raw is None:  # never existed, logged out, or removed when it expired
        return session_id, None
    record = json.loads(raw)
    if record["expires"] <= time.time():  # Harbor checks the expiration itself
        store.delete(f"session:{session_id}")
        return session_id, None
    return session_id, record


def save_session(session_id: str, record: dict):
    store.set(f"session:{session_id}", json.dumps(record), keepttl=True)


def session_cookie(session_id: str) -> str:
    return f"session={session_id}; Secure; HttpOnly; SameSite={lab('samesite', 'Lax')}; Path=/"


def cleared_cookie() -> str:
    return f"session=; Max-Age=0; Secure; HttpOnly; SameSite={lab('samesite', 'Lax')}; Path=/"


def signed_in(session_id: str) -> RedirectResponse:
    response = RedirectResponse("/", status_code=303)
    response.headers.append("Set-Cookie", session_cookie(session_id))
    return response


# ---- the second connection (sections 05 and 09): the backend calls the Status API -----------------------------------

def step(trace: list, who: str, detail: str):
    trace.append({"time": time.strftime("%H:%M:%S UTC", time.gmtime()), "step": who, "detail": detail})


def access_token_for(session_id: str, record: dict, trace: list) -> str | None:
    """Section 09: use the access token kept with the session; if it has expired, refresh it first."""
    left = int(record["access_expires"] - time.time())
    if left > 10:
        step(trace, "dashboard", f"takes the access token kept with the session (valid for another {left} s)")
        return record["access_token"]
    step(trace, "dashboard -> Harbor Sign-in", "the access token has expired: POST /token, grant_type=refresh_token, "
                                                "with the dashboard's client ID and secret")
    response = httpx.post(TOKEN, data={"grant_type": "refresh_token", "refresh_token": record["refresh_token"]},
                          auth=(CLIENT_ID, CLIENT_SECRET), timeout=10)
    if response.status_code != 200:
        step(trace, "Harbor Sign-in -> dashboard", f"{response.status_code}: {response.text[:200]}")
        return None
    tokens = response.json()
    record.update(access_token=tokens["access_token"], refresh_token=tokens.get("refresh_token", record["refresh_token"]),
                  access_expires=time.time() + tokens["expires_in"])
    save_session(session_id, record)
    step(trace, "Harbor Sign-in -> dashboard", f"a new access token, valid for {tokens['expires_in']} s; Maya never noticed")
    return record["access_token"]


def tracking_status(session_id: str, record: dict, trace: list) -> dict:
    if record.get("access_token"):  # signed in with Harbor (section 08): Maya's own access token
        token = access_token_for(session_id, record, trace)
        if token is None:  # no request reached the Status API
            return {"ok": False, "status": None, "text": "Harbor Sign-in refused to refresh the access token: sign in again"}
        what = "Maya's access token (a JWT from Harbor Sign-in)"
    else:  # signed in with the password form: the backend's own prepared token (section 05)
        token = API_TOKEN
        what = "the dashboard backend's prepared opaque token"
    step(trace, "dashboard -> Status API", f"GET /api/status/tracking, Authorization: Bearer {short(token, 10)} ({what})")
    response = httpx.get(f"{STATUS_API}/api/status/tracking", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    body = response.json()
    if response.headers.get("x-harbor-checked"):
        step(trace, "Status API", f"checked: {response.headers['x-harbor-checked']}")
    if response.status_code == 200:
        step(trace, "Status API -> dashboard", f"200: {body['service']}, {body['status']}")
        return {"ok": True, "status": 200, "text": f"{body['service']} — {body['status']}"}
    step(trace, "Status API -> dashboard", f"{response.status_code}: {body.get('reason')}")
    return {"ok": False, "status": response.status_code,
            "text": f"The Status API answered {response.status_code}: {body.get('reason')}"}


def refresh_status(request: Request, session_id: str, record: dict) -> dict:
    trace = []
    step(trace, "browser -> dashboard", f"{request.method} {request.url.path}, Cookie: session={short(session_id)}")
    step(trace, "dashboard", f"found the session in the shared store: {record['user']}, valid for another "
                             f"{int(record['expires'] - time.time())} s")
    result = tracking_status(session_id, record, trace)
    step(trace, "dashboard -> browser", result["text"])
    store.set(f"trace:{session_id}", json.dumps(trace), ex=3600)
    return result


# ---- pages ----------------------------------------------------------------------------------------------------------

@app.middleware("http")
async def remember_requests(request: Request, call_next):
    """Lab only: what reached the dashboard, for the lab's teaching view (/lab/requests)."""
    response = await call_next(request)
    response.headers["X-Harbor-Server"] = SERVER
    if not request.url.path.startswith(("/lab", "/health", "/favicon")):
        entry = {"time": time.strftime("%H:%M:%S UTC", time.gmtime()), "server": SERVER, "method": request.method,
                 "path": request.url.path,
                 "cookie": f"session={short(request.cookies['session'])}" if request.cookies.get("session") else "(none)",
                 "origin": request.headers.get("origin"), "sec-fetch-site": request.headers.get("sec-fetch-site"),
                 "status": response.status_code, "note": getattr(request.state, "note", None)}
        store.lpush("lab:requests", json.dumps(entry))
        store.ltrim("lab:requests", 0, 49)
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    session_id, record = find_session(request)
    if record is None:
        return RedirectResponse("/login", status_code=303)
    result = refresh_status(request, session_id, record)
    alerts_to = store.hget(f"alerts:{record['user']}", "alerts_to") or "maya@harbor.example"
    css = "ok" if result["ok"] else "no"
    return page("Harbor dashboard", f"""
<h1>Harbor dashboard</h1>
<p class=muted>Signed in as {escape(USERS[record['user']]['name'])}, with {escape(record.get('signed_in_with', 'a password'))}.
Served by {SERVER}.</p>
<div class=card><h2>Tracking service</h2><p class={css} id=status>{escape(result['text'])}</p>
<a class=button id=refresh href="/">Refresh</a></div>
<div class=card><h2>Status alerts</h2>
<form method=post action="/alerts"><label>Send my status alerts to
<input name=alerts_to value="{escape(alerts_to)}" size=30></label>
<input type=hidden name=csrf_token value="{escape(record['csrf_token'])}"><button id=save-alerts>Save</button></form></div>
<form class=inline method=post action="/logout">
<input type=hidden name=csrf_token value="{escape(record['csrf_token'])}"><button id=logout>Log out</button></form>
{lab_note('<a href="/lab/session">your session record</a> · <a href="/lab/sessions">every session</a> · '
          '<a href="/lab/requests">what the dashboard received</a> · <a href="/lab/trace">the last refresh, step by step</a>. '
          'A real dashboard has none of these pages.')}""")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str = ""):
    message = f"<p class=no>{escape(error)}</p>" if error else ""
    if lab("signin", "password") == "harbor":  # section 08: the company's sign-in service handles the login
        return page("Sign in: Harbor dashboard", f"""<h1>Harbor dashboard</h1>{message}
<p><a class=button id=sign-in-with-harbor href="/auth/start">Sign in with Harbor</a></p>""")
    return page("Sign in: Harbor dashboard", f"""<h1>Harbor dashboard</h1>{message}
<form method=post action="/login">
<label>Username <input name=username id=username autocomplete=username></label>
<label>Password <input name=password id=password type=password autocomplete=current-password></label>
<button id=sign-in>Sign in</button></form>
{lab_note('the password is <code>demo-only</code>. Never type a real password into a lab.')}""")


@app.post("/login")
def login(request: Request, username: str = Form(""), password: str = Form("")):
    if lab("signin", "password") == "harbor":  # section 08: the dashboard no longer checks passwords at all
        request.state.note = "password form refused: Harbor Sign-in handles the login"
        return HTMLResponse(login_page(request, "The password form is off: Harbor Sign-in handles the login now."),
                            status_code=403)
    user = USERS.get(username)
    try:  # the same slow hash check as Basic, once per sign-in instead of once per request
        hasher.verify(user["password_hash"] if user else NOBODY, password)
    except VerificationError:
        user = None
    if user is None:
        request.state.note = "wrong username or password"
        return HTMLResponse(login_page(request, "Wrong username or password."), status_code=401,
                            headers={"WWW-Authenticate": CHALLENGE})
    session_id, _ = create_session(username, signed_in_with="a password")
    request.state.note = f"signed in: new session {short(session_id)}"
    return signed_in(session_id)


@app.get("/status")
def status(request: Request):
    """The status card as JSON, for scripts and the terminal (the same check as the page)."""
    session_id, record = find_session(request)
    if record is None:
        request.state.note = "no valid session"
        return JSONResponse({"error": "unauthorized", "reason": "no valid session"}, status_code=401,
                            headers={"WWW-Authenticate": CHALLENGE})
    result = refresh_status(request, session_id, record)
    return {"status": result["text"], "ok": result["ok"], "served_by": SERVER}


@app.post("/alerts")
async def change_alerts(request: Request):
    """Maya's own setting: where her status alerts go, a change she is allowed to make. It changes data, so the cookie
    alone isn't enough (section 03): the request must also come from Harbor's own page."""
    form = await request.form()
    session_id, record = find_session(request)
    if record is None:
        request.state.note = "no valid session: rejected"
        origin = request.headers.get("origin")
        elsewhere = lab_note(f"This request came from {escape(origin)}, and the browser sent no session cookie with "
                             "it: a SameSite=Lax cookie stays off another site's POST. Maya's own sign-in is "
                             "untouched; her dashboard tab still works.") if origin and origin != DASHBOARD else ""
        return HTMLResponse(page("Not signed in", "<h1>Not signed in</h1><p class=no>No valid session came with this "
                                 "request, so Harbor doesn't know who is asking. Nothing was changed.</p>" + elsewhere),
                            status_code=401, headers={"WWW-Authenticate": CHALLENGE})
    refused = csrf_refusal(request, form, record)
    if refused:
        return refused
    store.hset(f"alerts:{record['user']}", "alerts_to", str(form.get("alerts_to", "")))
    request.state.note = "status alerts address changed"
    return RedirectResponse("/", status_code=303)


def csrf_refusal(request: Request, form, record: dict) -> HTMLResponse | None:
    """Section 03's check of Harbor's own, for every request that changes data: the request must come from Harbor's own
    page (its Origin) and carry this session's form token. Returns the refusal, or None when both pass."""
    origin = request.headers.get("origin")
    token = str(form.get("csrf_token", ""))
    failed = []
    if origin != DASHBOARD:
        failed.append(f"it didn't come from Harbor's own page (Origin: {origin})")
    if not secrets.compare_digest(token.encode(), record["csrf_token"].encode()):
        failed.append("it carried no valid form token for this session")
    if not failed:
        return None
    request.state.note = "CSRF check failed: " + " and ".join(failed)
    return HTMLResponse(page("Refused", f"<h1>Refused</h1><p class=no>Maya's cookie came with this request, but "
                             f"{escape(' and '.join(failed))}. Nothing was changed.</p>"), status_code=403)


@app.post("/logout")
async def logout(request: Request):
    form = await request.form()
    session_id, record = find_session(request)
    if record is not None:  # logging out changes data too, so it gets the same check
        refused = csrf_refusal(request, form, record)
        if refused:
            return refused
    if session_id:
        store.delete(f"session:{session_id}")  # invalidate the record: every copy of this ID stops working
        request.state.note = f"logged out: session {short(session_id)} deleted"
    response = RedirectResponse("/login", status_code=303)
    response.headers.append("Set-Cookie", cleared_cookie())  # and clear this browser's copy
    return response


# ---- Sign in with Harbor (section 08): OpenID Connect, the authorization code flow with PKCE ---------------------------

@app.get("/auth/start")
def sign_in_with_harbor():
    verifier, challenge = new_pkce()
    attempt = {"state": secrets.token_urlsafe(16), "nonce": secrets.token_urlsafe(16), "verifier": verifier}
    attempt_id = secrets.token_urlsafe(16)
    store.set(f"login_attempt:{attempt_id}", json.dumps(attempt), ex=300)
    url = AUTHORIZE + "?" + urlencode({
        "response_type": "code", "client_id": CLIENT_ID, "redirect_uri": CALLBACK, "scope": "openid status:read",
        "state": attempt["state"], "nonce": attempt["nonce"], "code_challenge": challenge, "code_challenge_method": "S256"})
    response = RedirectResponse(url, status_code=303)
    response.headers.append("Set-Cookie", f"login_attempt={attempt_id}; Secure; HttpOnly; SameSite=Lax; Path=/auth; Max-Age=300")
    return response


def refuse_sign_in(request: Request, why: str) -> HTMLResponse:
    request.state.note = f"sign-in refused: {why}"
    return HTMLResponse(page("Sign-in refused", f"<h1>Sign-in refused</h1><p class=no>{escape(why)}</p>"
                             "<p><a href='/login'>Start again</a></p>"), status_code=400)


@app.get("/auth/callback")
def callback(request: Request, code: str = "", state: str = "", error: str = ""):
    raw = store.getdel(f"login_attempt:{request.cookies.get('login_attempt', '')}")
    if raw is None:
        return refuse_sign_in(request, "This sign-in didn't start here, was already used, or took longer than 5 minutes.")
    attempt = json.loads(raw)
    if error:
        return refuse_sign_in(request, f"Harbor Sign-in answered: {error}")
    if not secrets.compare_digest(state.encode(), attempt["state"].encode()):  # this answer belongs to the attempt we started
        return refuse_sign_in(request, "The state doesn't match the sign-in this browser started.")
    # the direct connection: the code, the client's own credentials and the PKCE verifier
    response = httpx.post(TOKEN, data={"grant_type": "authorization_code", "code": code, "redirect_uri": CALLBACK,
                                       "code_verifier": attempt["verifier"]}, auth=(CLIENT_ID, CLIENT_SECRET), timeout=10)
    if response.status_code != 200:
        return refuse_sign_in(request, f"The code exchange failed: {response.text[:200]}")
    tokens = response.json()
    try:  # the ID token is for the dashboard: check its signature, issuer, audience and expiry
        key = JWKS.get_signing_key_from_jwt(tokens["id_token"])
        identity = jwt.decode(tokens["id_token"], key.key, algorithms=["RS256"], audience=CLIENT_ID, issuer=ISSUER,
                              options={"require": ["exp", "iss", "aud", "sub"]})
    except jwt.exceptions.PyJWTError as problem:
        return refuse_sign_in(request, f"The ID token didn't pass the checks: {problem}")
    if identity.get("nonce") != attempt["nonce"]:  # and it belongs to this sign-in attempt
        return refuse_sign_in(request, "The ID token's nonce doesn't match this sign-in attempt.")
    user = ACCOUNTS.get(identity["sub"])
    if user is None:
        return refuse_sign_in(request, f"No dashboard account for {identity['sub']}.")
    session_id, _ = create_session(user, signed_in_with="Harbor Sign-in", sub=identity["sub"],
                                   id_token=tokens["id_token"], access_token=tokens["access_token"],
                                   refresh_token=tokens["refresh_token"], access_expires=time.time() + tokens["expires_in"])
    request.state.note = f"signed in with Harbor: new session {short(session_id)}"
    response = signed_in(session_id)
    response.headers.append("Set-Cookie", "login_attempt=; Max-Age=0; Secure; HttpOnly; SameSite=Lax; Path=/auth")
    return response


@app.get("/health")
def health():
    store.ping()
    return {"ok": True, "server": SERVER}


# ---- lab only: teaching views and switches. A real dashboard has none of this. ------------------------------------------

def claims(token: str | None) -> dict | None:
    return jwt.decode(token, options={"verify_signature": False}) if token and token.count(".") == 2 else None


def when(timestamp: float) -> str:
    return time.strftime("%H:%M:%S UTC", time.gmtime(timestamp))


@app.get("/lab/session")
def lab_session(request: Request):
    session_id, record = find_session(request)
    if record is None:
        return JSONResponse({"lab_only": "no valid session came with this request"}, status_code=401,
                            headers={"WWW-Authenticate": CHALLENGE})
    # The toolbox's `harbor session` calls this server directly, not through the gateway browsers use, and gets the whole
    # token values, to send one on (mission 8). Through the gateway, the values stay shortened.
    full = admin(request) and "x-forwarded-for" not in request.headers
    show = (lambda token: token) if full else (lambda token: short(token, 12))
    view = {"lab_only": "Harbor's record for this session, kept on the server. A real dashboard has no page like this "
                        "one, so no page script can read the record. "
                        + ("The toolbox asked this server directly, so the token values are whole." if full else
                           "In this lab a script on the dashboard could fetch this view, so the token values are shortened."),
            "session_id": short(session_id), "user": record["user"], "signed_in_with": record.get("signed_in_with"),
            "created": when(record["created"]), "expires": when(record["expires"]),
            "expires_in_seconds": int(record["expires"] - time.time()), "created_by": record["created_by"],
            "csrf_token": short(record["csrf_token"])}
    if record.get("id_token"):
        view["tokens_kept_with_the_session"] = {
            "id_token": {"value": show(record["id_token"]), "claims": claims(record["id_token"])},
            "access_token": {"value": show(record["access_token"]), "claims": claims(record["access_token"]),
                             "expires_in_seconds": int(record["access_expires"] - time.time())},
            "refresh_token": {"value": show(record["refresh_token"]), "goes_only_to": "Harbor Sign-in"}}
    return view


@app.get("/lab/sessions")
def lab_sessions():
    out = []
    for key in store.scan_iter("session:*"):
        raw = store.get(key)
        if raw:
            record = json.loads(raw)
            out.append({"session_id": short(key.split(":", 1)[1]), "user": record["user"],
                        "signed_in_with": record.get("signed_in_with"), "created_by": record["created_by"],
                        "expires": when(record["expires"])})
    return {"lab_only": "every session record in the shared store", "sessions": out}


@app.get("/lab/requests")
def lab_requests():
    return [json.loads(x) for x in store.lrange("lab:requests", 0, 49)]


@app.get("/lab/trace")
def lab_trace(request: Request):
    session_id, record = find_session(request)
    raw = store.get(f"trace:{session_id}") if record else None
    return {"lab_only": "the last refresh of the status card, step by step", "steps": json.loads(raw) if raw else []}


def admin(request: Request) -> bool:
    return request.headers.get("x-lab-admin") == LAB_ADMIN


@app.post("/lab/config")
async def lab_config(request: Request):
    if not admin(request):
        return JSONResponse({"error": "lab admin only"}, status_code=403)
    changes = await request.json()
    allowed = {"samesite": {"Lax", "None", "Strict"}, "signin": {"password", "harbor"}}
    for name, value in changes.items():
        if name == "session_ttl" and str(value).isdigit() and int(value) > 0:
            store.set("lab:session_ttl", str(value))
        elif value in allowed.get(name, ()):
            store.set(f"lab:{name}", value)
        else:
            return JSONResponse({"error": f"can't set {name} to {value}"}, status_code=400)
    return {name: lab(name, default) for name, default in (("samesite", "Lax"), ("signin", "password"), ("session_ttl", "1800"))}


@app.post("/lab/reset")
def lab_reset(request: Request):
    """Every switch back to its starting value (`harbor lab reset`)."""
    if not admin(request):
        return JSONResponse({"error": "lab admin only"}, status_code=403)
    store.delete("lab:samesite", "lab:signin", "lab:session_ttl")
    return {"samesite": "Lax", "signin": "password", "session_ttl": "1800"}


@app.post("/lab/expire-access")
def lab_expire_access(request: Request):
    """Mark every session's access token as expired, so the next refresh shows the refresh step without a wait."""
    if not admin(request):
        return JSONResponse({"error": "lab admin only"}, status_code=403)
    marked = 0
    for key in store.scan_iter("session:*"):
        raw = store.get(key)
        record = json.loads(raw) if raw else {}
        if record.get("access_token"):
            record["access_expires"] = time.time() - 1
            store.set(key, json.dumps(record), keepttl=True)
            marked += 1
    return {"sessions_marked": marked}


@app.get("/lab/check")
def lab_check(request: Request):
    """Mission 9: what every signed-in dashboard session gets from the Status API right now."""
    if not admin(request):
        return JSONResponse({"error": "lab admin only"}, status_code=403)
    results = []
    for key in store.scan_iter("session:*"):
        session_id = key.split(":", 1)[1]
        raw = store.get(key)
        if raw and json.loads(raw)["expires"] > time.time():
            record = json.loads(raw)
            result = tracking_status(session_id, record, [])
            results.append({"session_id": short(session_id), "user": record["user"], **result})
    return results
