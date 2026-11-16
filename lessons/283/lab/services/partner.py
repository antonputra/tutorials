"""The partner's reporting application (section 07): a confidential OAuth client that uses PKCE.

Maya is already using the partner's site. When she presses Connect Harbor, this backend prepares the authorization
request, sends her browser to Harbor Sign-in, takes the code that comes back, and exchanges it on a direct connection,
with its client ID and secret and the PKCE verifier. Then it reads the tracking status with the access token.
Every step is written out with httpx and PyJWT, rather than an OAuth library, so each one can be read.
Lab code: one connection, kept in memory.
"""
import json
import os
import secrets
import time
from html import escape
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from common import AUTHORIZE, LAB_ADMIN, PARTNER, STATUS_API, TOKEN, lab_note, new_pkce, page, short

CLIENT_ID = "partner-reports"
CLIENT_SECRET = os.environ["PARTNER_CLIENT_SECRET"]
CALLBACK = f"{PARTNER}/callback"

app = FastAPI(title="Partner Reports")
ATTEMPTS: dict[str, dict] = {}  # connection attempts in progress, by the browser's connect_attempt cookie
CONNECTION: dict = {}           # Maya's connection: the tokens, kept on this backend, never in her browser
LAB = {"wrong_verifier": False, "log": []}


def note(text: str):
    LAB["log"].insert(0, {"time": time.strftime("%H:%M:%S UTC", time.gmtime()), "event": text})
    del LAB["log"][30:]


def read_status(access_token: str) -> tuple[int, dict]:
    response = httpx.get(f"{STATUS_API}/api/status/tracking", headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
    return response.status_code, response.json()


def use_refresh_token() -> tuple[bool, dict]:
    """A new access token for the refresh token. The refresh token goes only to Harbor Sign-in, never to the Status API."""
    response = httpx.post(TOKEN, data={"grant_type": "refresh_token", "refresh_token": CONNECTION["refresh_token"]},
                          auth=(CLIENT_ID, CLIENT_SECRET), timeout=10)
    answer = response.json()
    if response.status_code != 200:
        note(f"refresh refused: {answer.get('error')}: {answer.get('error_description')}")
        return False, {"status": response.status_code, **answer}
    CONNECTION.update(access_token=answer["access_token"], refresh_token=answer.get("refresh_token", CONNECTION["refresh_token"]),
                      access_expires=time.time() + answer["expires_in"])
    return True, answer


def access_token() -> tuple[str | None, str]:
    """The access token for the next call. Like Harbor's dashboard, refresh it first when it has (nearly) expired."""
    if CONNECTION["access_expires"] - time.time() > 10:
        return CONNECTION["access_token"], ""
    ok, answer = use_refresh_token()
    if not ok:
        return None, (f"The access token expired, and Harbor Sign-in refused to refresh it ({answer.get('error')}). "
                      "Connect Harbor again.")
    note("refresh: the access token had expired, so Harbor Sign-in gave a new one")
    return CONNECTION["access_token"], ""


def report_card() -> str:
    if not CONNECTION:
        return ""
    token, why = access_token()
    if token is None:
        return f"<div class=card><h2>Report</h2><p class=no id=report>{escape(why)}</p></div>"
    code, body = read_status(token)
    note(f"report: Bearer access token -> Status API: {code}")
    text = f"{body['service']} — {body['status']}" if code == 200 else f"The Status API answered {code}: {body.get('reason')}"
    return f"<div class=card><h2>Report</h2><p class={'ok' if code == 200 else 'no'} id=report>{escape(text)}</p></div>"


@app.get("/", response_class=HTMLResponse)
def home():
    if not CONNECTION:
        body = """<p>Connect your Harbor account to add Harbor's tracking status to your reports.</p>
<p><a class=button id=connect href="/connect">Connect Harbor</a></p>"""
    else:
        report = report_card()  # first: it may refresh the access token
        left = int(CONNECTION["access_expires"] - time.time())
        held = (f"The access token is valid for another {left} s." if left > 10 else
                "It has no working access token now: see the report above.")
        body = f"""{report}
<p class=muted>Connected to Harbor. {held}</p>
<a class=button id=refresh-report href="/">Refresh the report</a>
<form class=inline method=post action="/refresh"><button id=new-access-token>Get a new access token</button></form>
{lab_note('<form class=inline method=post action="/lab/refresh-token-to-api"><button id=refresh-token-to-api>'
          'Send the refresh token to the Status API</button></form> · <a href="/lab/tokens">the tokens this backend keeps</a>')}
<p class=muted><a id=connect href="/connect">Connect Harbor again</a></p>"""
    return page("Partner Reports", f"<h1>Partner Reports</h1>{body}")


@app.get("/connect", response_class=HTMLResponse)
def connect():
    """Connect Harbor: prepare the authorization request and show it before the browser goes anywhere."""
    verifier, challenge = new_pkce()
    state = secrets.token_urlsafe(16)
    params = {"response_type": "code", "client_id": CLIENT_ID, "redirect_uri": CALLBACK, "scope": "status:read",
              "state": state, "code_challenge": challenge, "code_challenge_method": "S256"}
    attempt_id = secrets.token_urlsafe(16)
    ATTEMPTS[attempt_id] = {"state": state, "verifier": verifier, "started": time.time()}
    note("Connect Harbor: a new state and PKCE verifier; the verifier stays on this backend")
    rows = "".join(f"<tr><td><code>{k}</code></td><td><code>{escape(v)}</code></td></tr>" for k, v in params.items())
    response = HTMLResponse(page("Connect Harbor", f"""<h1>Connect Harbor</h1>
<p>Your browser is about to go to Harbor Sign-in with this request:</p>
<div class=card><p><code>GET {escape(AUTHORIZE)}</code></p><table>{rows}</table></div>
<p class=muted>Not in the request: the PKCE verifier (<code>{short(verifier, 8)}</code>), which this backend keeps, and the
partner's client secret.</p>
<p><a class=button id=continue href="{escape(AUTHORIZE + '?' + urlencode(params))}">Continue to Harbor Sign-in</a></p>"""))
    response.headers.append("Set-Cookie", f"connect_attempt={attempt_id}; Secure; HttpOnly; SameSite=Lax; Path=/; Max-Age=600")
    return response


def problem(title: str, text: str, status: int = 400) -> HTMLResponse:
    note(f"{title}: {text}")
    return HTMLResponse(page(title, f"<h1>{escape(title)}</h1><p class=no>{escape(text)}</p><p><a href='/'>Back</a></p>"),
                        status_code=status)


@app.get("/callback", response_class=HTMLResponse)
def callback(request: Request, code: str = "", state: str = "", error: str = "", error_description: str = ""):
    response = finish_connecting(request, code, state, error, error_description)
    response.headers.append("Set-Cookie", "connect_attempt=; Max-Age=0; Secure; HttpOnly; SameSite=Lax; Path=/")  # attempt over
    return response


def finish_connecting(request: Request, code: str, state: str, error: str, error_description: str) -> HTMLResponse:
    attempt = ATTEMPTS.pop(request.cookies.get("connect_attempt", ""), None)  # each attempt is used once
    if attempt is None:
        if code and code == LAB.get("last_code", {}).get("code"):  # a reload: never send a code to Harbor Sign-in twice
            return problem("Code already used", "This address's code was already exchanged, and a code is used once. "
                                                "The connection is on the Partner Reports page.")
        return problem("Not connected", "This browser has no connection attempt waiting (it was already used, or never started).")
    if error:
        return problem("Not connected", f"Harbor Sign-in answered {error}: {error_description}")
    if not secrets.compare_digest(state.encode(), attempt["state"].encode()):
        return problem("Not connected", "The state doesn't match the attempt this browser started.")
    verifier = "wrong-" + attempt["verifier"] if LAB["wrong_verifier"] else attempt["verifier"]
    LAB["wrong_verifier"] = False  # the lab's extra spoils one connection, the next one
    sent ={"grant_type": "authorization_code", "code": code, "redirect_uri": CALLBACK, "code_verifier": verifier}
    response = httpx.post(TOKEN, data=sent, auth=(CLIENT_ID, CLIENT_SECRET), timeout=10)  # the direct connection
    answer = response.json()
    exchange = {"request": f"POST {TOKEN}", "client_authentication": f"Basic {CLIENT_ID}:{short(CLIENT_SECRET, 4)} (HTTP Basic)",
                "form": {**sent, "code": short(code, 10), "code_verifier": short(verifier, 8)},
                "answer": {"status": response.status_code,
                           **{k: (short(v, 12) if k.endswith("token") else v) for k, v in answer.items()}}}
    LAB["last_code"] = {"code": code, "verifier": attempt["verifier"]}  # lab only: for the "use the code again" extra
    if response.status_code != 200:
        note(f"code exchange refused: {answer.get('error')}: {answer.get('error_description')}")
        return HTMLResponse(page("Not connected", f"""<h1>Not connected</h1>
<p class=no>Harbor Sign-in refused the code exchange: <code>{escape(answer.get('error', ''))}</code>,
{escape(answer.get('error_description', ''))}</p>
<div class=card><h2>The backend's token exchange</h2><pre>{escape(pretty(exchange))}</pre></div><p><a href='/'>Back</a></p>"""),
                            status_code=400)
    CONNECTION.update(access_token=answer["access_token"], refresh_token=answer["refresh_token"],
                      access_expires=time.time() + answer["expires_in"], exchange=exchange)
    note("connected: code + client secret + verifier exchanged for an access token and a refresh token")
    return HTMLResponse(page("Connected to Harbor", f"""<h1>Connected to Harbor</h1>
<p>Harbor Sign-in sent your browser back here with a code in the address: <code>{escape(short(code, 10))}</code>.
The browser carried only that code.</p>
<div class=card><h2>The backend's token exchange</h2><pre id=exchange>{escape(pretty(exchange))}</pre></div>
{report_card()}<p><a class=button id=home href="/">Go to Partner Reports</a></p>"""))


def pretty(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


@app.post("/refresh", response_class=HTMLResponse)
def refresh():
    """Get a new access token with the refresh token: it goes only to Harbor Sign-in, never to the Status API."""
    if not CONNECTION:
        return problem("Not connected", "Connect Harbor first.")
    ok, answer = use_refresh_token()
    if not ok:
        return problem("Refresh refused", f"Harbor Sign-in answered {answer['status']}: {answer.get('error')}, "
                                          f"{answer.get('error_description')}")
    note("refresh: Harbor Sign-in gave a new access token")
    return page("New access token", f"""<h1>New access token</h1>
<p class=ok id=refreshed>Harbor Sign-in gave a new access token for the refresh token, valid for {answer['expires_in']} s.
Maya didn't have to sign in again.</p><p><a class=button href="/">Back to the report</a></p>""")


@app.get("/health")
def health():
    return {"ok": True}


# ---- lab only: teaching views and the extras. A real partner app has none of this. ----------------------------------

def admin(request: Request) -> bool:
    return request.headers.get("x-lab-admin") == LAB_ADMIN


@app.post("/lab/refresh-token-to-api", response_class=HTMLResponse)
def refresh_token_to_api():
    if not CONNECTION:
        return problem("Not connected", "Connect Harbor first.")
    code, body = read_status(CONNECTION["refresh_token"])
    note(f"lab: the refresh token sent to the Status API: {code}")
    return page("The refresh token at the Status API", f"""<h1>The refresh token at the Status API</h1>
<p class={'ok' if code == 200 else 'no'} id=refresh-token-answer>The Status API answered {code}: {escape(str(body.get('reason', body)))}</p>
<p>A refresh token is only for Harbor Sign-in.</p><p><a class=button href="/">Back</a></p>""")


@app.get("/lab/tokens")
def lab_tokens(request: Request):
    if not CONNECTION:
        return {"lab_only": "not connected", "log": LAB["log"]}
    full = admin(request) and "x-forwarded-for" not in request.headers  # whole values only to the toolbox, asking directly
    view = {"lab_only": "the tokens this backend keeps for Maya's connection; her browser never receives them. A real "
                        "partner app has no page like this one. "
                        + ("The toolbox asked this server directly, so the values are whole." if full else
                           "Through the gateway, the values are shortened."),
            "access_token": CONNECTION["access_token"] if full else short(CONNECTION["access_token"], 12),
            "access_token_claims": jwt.decode(CONNECTION["access_token"], options={"verify_signature": False}),
            "access_token_expires_in_seconds": int(CONNECTION["access_expires"] - time.time()),
            "refresh_token": CONNECTION["refresh_token"] if full else short(CONNECTION["refresh_token"], 12),
            "refresh_token_goes_only_to": "Harbor Sign-in", "last_exchange": CONNECTION.get("exchange"), "log": LAB["log"]}
    return view


@app.get("/lab/check")
def lab_check(request: Request):
    """Mission 9: what the partner's access token gets from the Status API right now."""
    if not admin(request):
        return JSONResponse({"error": "lab admin only"}, status_code=403)
    if not CONNECTION:
        return {"status": "-", "text": "the partner isn't connected"}
    token, why = access_token()
    if token is None:
        return {"status": "-", "text": why}
    code, body = read_status(token)
    return {"status": code, "text": f"{body['service']} — {body['status']}" if code == 200 else body.get("reason")}


@app.post("/lab/wrong-verifier/{on}")
def lab_wrong_verifier(on: str, request: Request):
    if not admin(request) or on not in ("on", "off"):
        return JSONResponse({"error": "lab admin only; on or off"}, status_code=403)
    LAB["wrong_verifier"] = on == "on"
    return {"wrong_verifier_on_the_next_connection": LAB["wrong_verifier"]}


@app.post("/lab/forget")
def lab_forget(request: Request):
    """Lab only, for the checks at their end: the partner's app as on a first visit, with no connection kept."""
    if not admin(request):
        return JSONResponse({"error": "lab admin only"}, status_code=403)
    CONNECTION.clear()
    ATTEMPTS.clear()
    LAB.update(wrong_verifier=False, log=[])
    LAB.pop("last_code", None)
    return {"partner": "no connection kept"}


@app.post("/lab/exchange-again")
def lab_exchange_again(request: Request):
    """The extra, run last: send the last code again. Harbor Sign-in refuses it, and cancels what the code gave."""
    if not admin(request) or not LAB.get("last_code"):
        return JSONResponse({"error": "lab admin only, after a connection"}, status_code=403)
    last = LAB["last_code"]
    again = httpx.post(TOKEN, data={"grant_type": "authorization_code", "code": last["code"], "redirect_uri": CALLBACK,
                                    "code_verifier": last["verifier"]}, auth=(CLIENT_ID, CLIENT_SECRET), timeout=10)
    out = {"code_used_again": {"status": again.status_code, **again.json()}}
    if CONNECTION:  # what the first exchange gave: Harbor Sign-in cancels it when a code comes back (RFC 6749, 4.1.2)
        first_access_token = CONNECTION["access_token"]
        ok, refreshed = use_refresh_token()
        out["the_first_refresh_token_now_gets"] = ("200: a new access token" if ok else
                                                   f"{refreshed['status']}: {refreshed.get('error')}, "
                                                   f"{refreshed.get('error_description')}")
        api = httpx.get(f"{STATUS_API}/api/status/tracking", headers={"Authorization": f"Bearer {first_access_token}"},
                        timeout=10)
        body = api.json()
        out["the_first_access_token_at_the_status_api"] = f"{api.status_code}: " + (
            f"{body['service']} — {body['status']}" if api.status_code == 200 else str(body.get("reason")))
        out["what_the_status_api_checked"] = api.headers.get("x-harbor-checked", "-")
    note(f"lab: the code sent again: {again.status_code}")
    return out
