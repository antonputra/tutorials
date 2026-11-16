#!/usr/bin/env python3
"""Every mission's outcomes, end to end, against the running Harbor lab.

    docker compose --profile tests run --rm tests              # about 15 s, on a freshly started lab
    docker compose --profile tests run --rm -e SLOW=1 tests    # also waits for a revoked token's exp (5 more minutes)

It runs where the toolbox runs (the gateway's network), types the toolbox's own commands (curl, base64 and the harbor
helpers) and plays the browser with a small scripted one for the steps a learner does on a page. What the real browsers
do (cookies, SameSite, what a page script can see) is checked by browsers.py, with Chromium and Firefox.
Prints PASS or FAIL for every check and exits 1 if any failed. Lab values only.
"""
import json
import os
import re
import statistics
import subprocess
import sys
import time
from html import unescape
from urllib.parse import parse_qs, urljoin, urlparse

import httpx
import jwt
import valkey

from common import AUTHORIZE, DASHBOARD, ISSUER, LAB_ADMIN, PARTNER, STATUS_API, short

API = f"{STATUS_API}/api/status/tracking"
SETTINGS = f"{STATUS_API}/api/settings/tracking"
COUPONS = f"http://coupons.localhost:{urlparse(DASHBOARD).port}"
ADMIN = {"X-Lab-Admin": LAB_ADMIN}
DASH_HOST = urlparse(DASHBOARD).hostname
HEALTHY = "Tracking service — Healthy"
SLOW = os.environ.get("SLOW") == "1"
FAILED: list[str] = []
COUNT = 0


def check(name: str, ok, detail=""):
    global COUNT
    COUNT += 1
    print(f"{'PASS' if ok else 'FAIL'}  {name}", flush=True)
    if not ok:
        FAILED.append(name)
        print("      " + str(detail)[:1500].replace("\n", "\n      "), flush=True)


def mission(title: str):
    print(f"\n== {title}", flush=True)


def sh(command: str) -> tuple[str, str]:
    """A line typed in the toolbox's terminal: (stdout, stderr)."""
    done = subprocess.run(["bash", "-c", command], capture_output=True, text=True, timeout=120)
    return done.stdout, done.stderr


def curl(args: str) -> str:
    """curl -si: the status line, the headers and the body, as the learner sees them."""
    return sh(f"curl -si {args}")[0].replace("\r\n", "\n")


def status_of(curl_output: str) -> int:
    match = re.match(r"HTTP/[\d.]+ (\d{3})", curl_output)
    return int(match.group(1)) if match else 0


def body_of(curl_output: str) -> dict:
    try:
        return json.loads(curl_output.split("\n\n", 1)[1])
    except (IndexError, ValueError):
        return {}


def header(curl_output: str, name: str) -> str:
    match = re.search(rf"(?im)^{re.escape(name)}: (.*)$", curl_output.split("\n\n", 1)[0])
    return match.group(1).strip() if match else ""


def text_of(html: str) -> str:
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


class Browser:
    """A scripted browser: keeps each host's cookies (Secure ones too: *.localhost is a secure context in a browser),
    follows no redirect by itself, and sends the headers a page's form would."""

    def __init__(self):
        self.jar: dict[str, dict] = {}
        self.http = httpx.Client(timeout=30, follow_redirects=False)

    def send(self, method: str, url: str, data=None, headers=None) -> httpx.Response:
        host = urlparse(url).hostname
        sent = dict(headers or {})
        if self.jar.get(host):
            sent["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.jar[host].items())
        response = self.http.request(method, url, data=data, headers=sent)
        for line in response.headers.get_list("set-cookie"):
            name, _, value = line.split(";", 1)[0].partition("=")
            if re.search(r"max-age=0\b|expires=thu, 01[- ]jan[- ]1970", line, re.I):
                self.jar.setdefault(host, {}).pop(name.strip(), None)
            else:
                self.jar.setdefault(host, {})[name.strip()] = value.strip()
        self.http.cookies.clear()
        return response

    def get(self, url: str, headers=None) -> httpx.Response:
        return self.send("GET", url, headers=headers)

    def post(self, url: str, data=None, headers=None) -> httpx.Response:
        return self.send("POST", url, data=data, headers=headers)

    def cookie(self, host: str, name: str) -> str | None:
        return self.jar.get(host, {}).get(name)


def form_parts(html: str) -> tuple[str, dict]:
    action = unescape(re.search(r'<form[^>]*\saction="([^"]+)"', html).group(1))
    hidden = {}
    for tag in re.findall(r"<input\b[^>]*>", html):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
        if attrs.get("type") == "hidden" and attrs.get("name"):
            hidden[attrs["name"]] = unescape(attrs.get("value", ""))
    return action, hidden


def through_harbor_sign_in(browser: Browser, response: httpx.Response, back_to: str) -> tuple[str | None, list]:
    """From Harbor Sign-in's first answer to the redirect back to `back_to`: Maya's password, then consent if asked.
    Returns (the address the browser is sent back to, the pages seen on the way)."""
    seen = []
    for _ in range(8):
        if response.status_code in (302, 303):
            location = urljoin(str(response.request.url), response.headers["location"])
            if location.startswith(back_to):
                return location, seen
            response = browser.get(location)
            continue
        html = response.text
        if response.status_code != 200 or "<form" not in html:
            seen.append(f"status {response.status_code}: {text_of(html)[:300]}")
            return None, seen
        action, hidden = form_parts(html)
        action = urljoin(str(response.request.url), action)
        if 'name="password"' in html:
            seen.append(f"password form at {urlparse(action).hostname}")
            response = browser.post(action, {**hidden, "username": "maya", "password": "demo-only", "credentialId": ""})
        elif 'name="accept"' in html:
            seen.append("consent: " + text_of(html))
            response = browser.post(action, {**hidden, "accept": "Yes"})
        else:
            seen.append("an unexpected form: " + text_of(html)[:300])
            return None, seen
    return None, seen


def password_sign_in(browser: Browser) -> tuple[httpx.Response, str | None]:
    response = browser.post(f"{DASHBOARD}/login", {"username": "maya", "password": "demo-only"})
    return response, browser.cookie(DASH_HOST, "session")


def alerts_to(browser: Browser) -> str:
    match = re.search(r'name=alerts_to value="([^"]*)"', browser.get(f"{DASHBOARD}/").text)
    return unescape(match.group(1)) if match else "(no settings form)"


def csrf_token(browser: Browser) -> str:
    match = re.search(r'name=csrf_token value="([^"]+)"', browser.get(f"{DASHBOARD}/").text)
    return unescape(match.group(1)) if match else ""


def connect_partner(browser: Browser) -> tuple[dict, list, httpx.Response | None]:
    """Mission 7's page steps: Connect Harbor, Continue, Harbor Sign-in, back to the partner's callback."""
    page = browser.get(f"{PARTNER}/connect")
    params = dict(re.findall(r"<tr><td><code>([^<]+)</code></td><td><code>([^<]*)</code></td></tr>", page.text))
    params = {k: unescape(v) for k, v in params.items()}
    link = re.search(r'id=continue href="([^"]+)"', page.text)
    if not link:
        return params, ["no Continue link on the Connect Harbor page"], None
    back, seen = through_harbor_sign_in(browser, browser.get(unescape(link.group(1))), f"{PARTNER}/callback")
    params["_continue"], params["_back"] = unescape(link.group(1)), back or ""
    return params, seen, (browser.get(back) if back else None)


def logout(browser: Browser, origin: str = DASHBOARD) -> httpx.Response:
    """The dashboard's Log out button: its form carries the session's form token, and the browser adds the Origin."""
    return browser.post(f"{DASHBOARD}/logout", {"csrf_token": csrf_token(browser)}, headers={"Origin": origin})


def signed_with_lab_key(claims: dict) -> str:
    """A token Harbor Sign-in's own (lab) key signed, for the checks that need unusual claims."""
    with open("/lab-keys/signing-key.pem", "rb") as f:
        return jwt.encode(claims, f.read(), algorithm="RS256", headers={"kid": lab_key["kid"]})


def seconds_to_refuse(username: str) -> float:
    """The median time the dashboard's password form takes to refuse this username with a wrong password."""
    times = []
    for _ in range(5):
        started = time.perf_counter()
        httpx.post(f"{DASHBOARD}/login", data={"username": username, "password": "not-the-password"}, timeout=10)
        times.append(time.perf_counter() - started)
    return statistics.median(times)


def check_rows(output: str) -> dict:
    """`harbor check`'s table: who -> (status, text)."""
    rows = {}
    for line in output.splitlines():
        match = re.match(r"^(.+?)\s+(\d{3}|-)\s+(.*)$", line)
        if match:
            rows[match.group(1).strip()] = (match.group(2), match.group(3))
    return rows


def the_end():
    """The switches back at their starting values, a working key for the job, and the partner as on a first visit (no
    connection, no grant), so mission 7 starts with Connect Harbor and the consent screen. It also runs when a check
    crashes part-way (crashed(), below). Maya's sessions, the job's other keys and the request logs stay."""
    mission("The end: the switches back, the partner disconnected")
    sh("harbor lab reset")
    sh("harbor partner disconnect")
    forgot = httpx.post(f"{PARTNER}/lab/forget", headers=ADMIN, timeout=10)
    home = Browser().get(f"{PARTNER}/")
    check("end: the partner keeps no connection: its page offers Connect Harbor",
          forgot.status_code == 200 and "Connect Harbor" in text_of(home.text) and "Connected to Harbor" not in text_of(home.text),
          text_of(home.text)[:300])
    gone, _ = sh("harbor partner disconnect")  # a second removal finds no grant left
    check("end: Harbor Sign-in keeps no grant for the partner: the next connection asks for consent",
          gone.startswith("answer 404") and "Consent nor offline token not found" in gone, gone)
    print("      The checks signed Maya in and rotated the job's key: before the missions or a capture, start from nothing "
          "(docker compose down -v, then docker compose up -d --wait).", flush=True)


def summary():
    print(f"\n{COUNT - len(FAILED)} of {COUNT} checks passed" + (f"; failed: {', '.join(FAILED)}" if FAILED else ""), flush=True)


def crashed(kind, value, trace):
    """A check that raised instead of failing: print the error, count the crash as a failed check, then still put the lab back."""
    global COUNT
    sys.__excepthook__(kind, value, trace)
    COUNT += 1
    FAILED.append(f"the checks stopped part-way ({kind.__name__})")
    try:
        the_end()
    except Exception as error:  # the lab may be down; the summary still prints
        print(f"      the end couldn't run: {type(error).__name__}: {error}", flush=True)
    summary()


sys.excepthook = crashed

# ---------------------------------------------------------------------------------------------------------------------

mission("Before the missions: the lab answers, and its switches are at their starting values")
for name, url in (("Harbor Sign-in", f"{ISSUER}/.well-known/openid-configuration"), ("the Status API", f"{STATUS_API}/health"),
                  ("the dashboard", f"{DASHBOARD}/health"), ("the partner", f"{PARTNER}/health"), ("the coupons site", f"{COUPONS}/")):
    try:
        code = httpx.get(url, timeout=10).status_code
    except httpx.HTTPError as error:
        code = f"{type(error).__name__}: {error}"
    check(f"{name} answers at {urlparse(url).netloc}", code == 200, code)
discovery = httpx.get(f"{ISSUER}/.well-known/openid-configuration", timeout=10).json()
check("Harbor Sign-in's issuer is the same address inside the network and in the browser", discovery["issuer"] == ISSUER,
      discovery["issuer"])
published = httpx.get(discovery["jwks_uri"], timeout=10).json()["keys"]
with open("/lab-keys/jwks.json") as f:
    lab_key = json.load(f)["keys"][0]
check("Harbor Sign-in publishes the lab's own signing key (the prepared tokens' key)",
      any(k["kid"] == lab_key["kid"] and k["n"] == lab_key["n"] for k in published), [k["kid"] for k in published])
_, err = sh("harbor lab reset")  # a run on a used lab: every switch back, and a working key for the job
config = httpx.post(f"{DASHBOARD}/lab/config", headers=ADMIN, json={}, timeout=10).json()
check("harbor lab reset: the password form, SameSite=Lax, 30-minute sessions, local JWT checks, the job's key active",
      config == {"samesite": "Lax", "signin": "password", "session_ttl": "1800"}
      and httpx.get(f"{STATUS_API}/lab/jwt-check", timeout=10).json() == {"jwt_check": "local"}
      and json.loads(sh("harbor key show")[0])[-1]["active"] and "Back to the starting values" in err, (config, err))


mission("Mission 1: the first private request (public exercise)")
out = curl(API)
check("1 no credentials: 401 with WWW-Authenticate: Basic", status_of(out) == 401 and header(out, "www-authenticate").startswith("Basic"),
      out)
out, err = sh(f"curl -s -v -u maya:demo-only {API}")
check("1 maya / demo-only: 200, Tracking service, Healthy",
      "< HTTP/1.1 200" in err and json.loads(out or "{}") == {"service": "Tracking service", "status": "Healthy"}, err + out)
check("1 the header curl sent: Authorization: Basic bWF5YTpkZW1vLW9ubHk=", "> Authorization: Basic bWF5YTpkZW1vLW9ubHk=" in err, err)
out, _ = sh("echo bWF5YTpkZW1vLW9ubHk= | base64 -d")
check("1 decoded, it is maya:demo-only (Base64 hides nothing)", out == "maya:demo-only", out)
out = curl(f"-u maya:not-the-password {API}")
check("1 a wrong password: 401", status_of(out) == 401 and body_of(out).get("reason") == "wrong username or password", out)
log = [json.loads(line) for line in sh("harbor requests 5")[0].split("\n") if line.strip()]  # not splitlines(): a header may hold U+0085
check("1 the Status API's record shows the header exactly as it arrived",
      any(e["status"] == 200 and e["authorization"] == "Basic bWF5YTpkZW1vLW9ubHk=" for e in log), log)


mission("Mission 5: the reporting job's own key (public exercise)")
out, err = sh("harbor job")
check("5 the job's key reads the status: 200", "< HTTP/1.1 200" in err and "Healthy" in out and "> X-API-Key: job_demo_" in err,
      err + out)
out, err = sh("harbor job --change")
check("5 the same key asks to change a setting: 403 Forbidden",
      "< HTTP/1.1 403 Forbidden" in err and "reporting job may not change" in out, err + out)
out, err = sh("harbor job --key job_demo_made_up_by_me")
check("5 a made-up key: 401", "< HTTP/1.1 401" in err and "unknown API key" in out, err + out)
check("5 ... with WWW-Authenticate: ApiKey, naming the header the key goes in",
      '< Www-Authenticate: ApiKey realm="Harbor", header="X-API-Key"' in err, err)
keys = json.loads(sh("harbor key show")[0])
check("5 the key's record: the reporting job, status:read, active",
      keys[-1]["owner"] == "reporting job" and keys[-1]["permissions"] == ["status:read"] and keys[-1]["active"], keys)
old_key = keys[-1]["key"]
new_key = json.loads(sh("harbor key rotate")[0])["new_key"]
out, err = sh("harbor job")
check("5 extra: after the rotation the job's new key works", "< HTTP/1.1 200" in err and f"> X-API-Key: {new_key}" in err, err)
out, err = sh(f"harbor job --key {old_key}")
check("5 extra: the old key is refused: 401", "< HTTP/1.1 401" in err and "this API key was revoked" in out, err + out)


mission("Mission 6: Bearer tokens and JWTs (the prepared-token steps are public)")
opaque = sh("harbor token --opaque")[0].strip()
out = curl(f'-H "Authorization: Bearer {opaque}" {API}')
check("6 the prepared opaque token as Bearer: 200, after the API looked it up",
      status_of(out) == 200 and header(out, "x-harbor-checked").startswith("opaque token: looked up, active"), out)
token = sh("harbor token")[0].strip()
decoded, _ = sh(f"harbor jwt decode {token}")
check("6 decoding shows iss, sub, aud, exp and scope", all(f'"{c}"' in decoded for c in ("iss", "sub", "aud", "exp", "scope"))
      and ISSUER in decoded and '"aud": "harbor-status-api"' in decoded and '"scope": "status:read"' in decoded, decoded)
out = curl(f'-H "Authorization: Bearer {token}" {API}')
check("6 the prepared JWT: 200 after the signature, issuer, audience and expiry checks",
      status_of(out) == 200 and header(out, "x-harbor-checked").startswith("JWT: signature (key "), out)
out = curl(f'-X PUT -H "Authorization: Bearer {token}" {SETTINGS}')
check("6 the same token asks to change settings: 403, and its challenge names the missing scope (RFC 6750)",
      status_of(out) == 403
      and header(out, "www-authenticate") == 'Bearer realm="Harbor", error="insufficient_scope", scope="settings:write"', out)
tampered = sh(f'harbor jwt edit {token} scope="status:read settings:write"')[0].strip()
check("6 the edited token still decodes, with the new scope (decoding isn't verifying)",
      '"scope": "status:read settings:write"' in sh(f"harbor jwt decode {tampered}")[0])
out = curl(f'-X PUT -H "Authorization: Bearer {tampered}" {SETTINGS}')
check("6 the tampered token asks to change settings: 401, the signature doesn't match",
      status_of(out) == 401 and body_of(out).get("reason") == "the signature doesn't match the token's content", out)
other = sh("harbor token --other-api")[0].strip()
out = curl(f'-H "Authorization: Bearer {other}" {API}')
check("6 a token made for another API: 401 (audience)",
      status_of(out) == 401 and body_of(out).get("reason") == "the token was made for harbor-billing-api, not for harbor-status-api", out)
expired = sh("harbor token --expired")[0].strip()
out = curl(f'-H "Authorization: Bearer {expired}" {API}')
check("6 an expired token: 401", status_of(out) == 401 and body_of(out).get("reason") == "the token has expired", out)
now = int(time.time())
stale_id_token = signed_with_lab_key({"exp": now - 600, "iat": now - 900, "iss": ISSUER, "aud": "harbor-dashboard",
                                      "sub": "maya-01", "typ": "ID"})
out = curl(f'-H "Authorization: Bearer {stale_id_token}" {API}')
check("6 a token made for another client and long expired: still refused for its audience (the expiry is checked last)",
      status_of(out) == 401 and body_of(out).get("reason") == "the token was made for harbor-dashboard, not for harbor-status-api",
      out)
fresh, fresh_steps = sh("harbor token --fresh")
fresh = fresh.strip()
check("6 harbor token --fresh shows each request of its sign-in: Harbor Sign-in's page, the form, the code exchange",
      f"> GET {AUTHORIZE}" in fresh_steps and "(form: username=maya&password=demo-only" in fresh_steps
      and "< 302 Found, Location: " in fresh_steps and "> POST " in fresh_steps and "code_verifier=" in fresh_steps
      and fresh_steps.rstrip().endswith("< 200 OK") and "The access token:" not in fresh_steps, fresh_steps)
fresh_claims = json.loads(re.search(r"payload: (\{.*?\n\})", sh(f"harbor jwt decode {fresh}")[0], re.S).group(1))
check("6 a fresh token from Harbor Sign-in: Maya's, for the Status API, 5 minutes",
      fresh_claims["sub"] == "maya-01" and fresh_claims["aud"] == "harbor-status-api" and fresh_claims["exp"] - fresh_claims["iat"] == 300,
      fresh_claims)
check("6 the fresh token: 200", status_of(curl(f'-H "Authorization: Bearer {fresh}" {API}')) == 200)
out, err = sh(f"harbor revoke {fresh}")
check("6 revoked at Harbor Sign-in: 200", "< HTTP/1.1 200" in err, err + out)
out = curl(f'-H "Authorization: Bearer {fresh}" {API}')
check("6 the revoked JWT still gets 200 (the API checks it locally, until its exp)", status_of(out) == 200, out)
sh("harbor api-check introspect")
out = curl(f'-H "Authorization: Bearer {fresh}" {API}')
check("6 extra: with introspection the revoked token fails at once: 401",
      status_of(out) == 401 and body_of(out).get("reason") == "Harbor Sign-in says this token is no longer active", out)
another = sh("harbor token --fresh")[0].strip()
out = curl(f'-H "Authorization: Bearer {another}" {API}')
check("6 extra: with introspection a token that wasn't revoked: 200, and Harbor Sign-in says it's active",
      status_of(out) == 200 and "Harbor Sign-in says it's still active" in header(out, "x-harbor-checked"), out)
sh("harbor api-check local")
check("6 back to local checks: the revoked token is accepted again until its exp",
      status_of(curl(f'-H "Authorization: Bearer {fresh}" {API}')) == 200)


mission("Mission 2: a browser login")
b = Browser()
r = b.get(f"{DASHBOARD}/")
check("2 signed out, the dashboard sends the browser to its sign-in page", r.status_code == 303 and r.headers.get("location") == "/login",
      r.status_code)
r = b.get(f"{DASHBOARD}/login")
check("2 the sign-in page: the password form", r.status_code == 200 and "id=username" in r.text and "id=password" in r.text)
r = b.post(f"{DASHBOARD}/login", {"username": "maya", "password": "not-the-password"})
check("2 a wrong password: 401 and no cookie", r.status_code == 401 and not r.headers.get_list("set-cookie"), r.status_code)
known, unknown = seconds_to_refuse("maya"), seconds_to_refuse("nobody-by-this-name")
check("2 an unknown username takes as long to refuse as a wrong password (one hash check either way)",
      unknown < known * 1.5, f"maya: {known * 1000:.0f} ms, an unknown name: {unknown * 1000:.0f} ms")
r, sid = password_sign_in(b)
set_cookie = r.headers.get("set-cookie", "")
check("2 Set-Cookie: session=...; Secure; HttpOnly; SameSite=Lax; Path=/",
      r.status_code == 303 and re.fullmatch(r"session=[A-Za-z0-9_-]{43}; Secure; HttpOnly; SameSite=Lax; Path=/", set_cookie), set_cookie)
r = b.get(f"{DASHBOARD}/")
check("2 the status card: Tracking service — Healthy", r.status_code == 200 and HEALTHY in r.text, text_of(r.text)[:300])
entry = next((e for e in httpx.get(f"{DASHBOARD}/lab/requests", timeout=10).json() if e["path"] == "/" and e["method"] == "GET"), {})
check("2 the next request carried Cookie: session=..., no password", entry.get("cookie", "").startswith("session=") and entry["status"] == 200,
      entry)
view = b.get(f"{DASHBOARD}/lab/session").json()
check("2 the server's record: Maya and an expiry time", view.get("user") == "maya" and 1790 <= view.get("expires_in_seconds", 0) <= 1800
      and view.get("signed_in_with") == "a password", view)
servers, codes = set(), set()
for _ in range(4):
    r = b.get(f"{DASHBOARD}/status")
    servers.add(r.headers.get("x-harbor-server"))
    codes.add(r.status_code)
check("2 extra: both dashboard servers accept the same cookie (one shared session store)",
      servers == {"dashboard-a", "dashboard-b"} and codes == {200}, (servers, codes))


mission("Mission 3: a request from another site")
r = httpx.get(f"{COUPONS}/", timeout=10)
check("3 the coupons page is another site, with a hidden form that changes where Maya's status alerts go",
      r.status_code == 200 and f'action="{DASHBOARD}/alerts"' in r.text and 'name="alerts_to"' in r.text)
before = alerts_to(b)
r = httpx.post(f"{DASHBOARD}/alerts", data={"alerts_to": "deals@coupons.example"},
               headers={"Origin": COUPONS, "Sec-Fetch-Site": "cross-site"}, timeout=10)
check("3 the forged request as it arrives with SameSite=Lax (no cookie): 401, nothing changed",
      r.status_code == 401 and alerts_to(b) == before, (r.status_code, alerts_to(b)))
check("3 ... and its 401 names how to sign in: WWW-Authenticate: Cookie (RFC 9110 asks every 401 for a challenge)",
      r.headers.get("www-authenticate", "").startswith('Cookie realm="Harbor dashboard"'), r.headers.get("www-authenticate"))
r = b.post(f"{DASHBOARD}/alerts", {"alerts_to": "deals@coupons.example"}, headers={"Origin": COUPONS})
check("3 extra: with Maya's cookie (SameSite=None) but from another site: 403, nothing changed",
      r.status_code == 403 and alerts_to(b) == before, (r.status_code, alerts_to(b)))
entry = next((e for e in httpx.get(f"{DASHBOARD}/lab/requests", timeout=10).json() if e["path"] == "/alerts"), {})
check("3 extra: the dashboard's record says why: the CSRF check (Origin, form token)",
      entry.get("note") == f"CSRF check failed: it didn't come from Harbor's own page (Origin: {COUPONS}) "
                           "and it carried no valid form token for this session", entry)
r = b.post(f"{DASHBOARD}/alerts", {"alerts_to": "deals@coupons.example", "csrf_token": "not-this-sessions-token"},
           headers={"Origin": DASHBOARD})
check("3 extra: Harbor's own Origin with a wrong form token: 403, and the page names only the form token",
      r.status_code == 403 and "no valid form token" in text_of(r.text) and "Harbor's own page" not in text_of(r.text)
      and alerts_to(b) == before, text_of(r.text)[:300])
r = b.post(f"{DASHBOARD}/alerts", {"alerts_to": "ops@harbor.example", "csrf_token": csrf_token(b)}, headers={"Origin": DASHBOARD})
check("3 Harbor's own form (its Origin and the session's form token) changes Maya's alerts address",
      r.status_code == 303 and alerts_to(b) == "ops@harbor.example", r.status_code)
b.post(f"{DASHBOARD}/alerts", {"alerts_to": before, "csrf_token": csrf_token(b)}, headers={"Origin": DASHBOARD})
sh("harbor lab samesite none")
r, _ = password_sign_in(Browser())
check("3 extra: harbor lab samesite none: the next sign-in's cookie says SameSite=None",
      "; SameSite=None; " in r.headers.get("set-cookie", ""), r.headers.get("set-cookie"))
sh("harbor lab samesite lax")


mission("Mission 4: log out and replay")
b4 = Browser()
_, first = password_sign_in(b4)
out, err = sh(f"harbor replay {first}")
check("4 the session ID replayed from the terminal works while signed in: 200", "< HTTP/1.1 200" in err, err + out)
r = logout(b4, origin=COUPONS)
check("4 a Log out sent from another site, with the cookie: 403, and Maya stays signed in",
      r.status_code == 403 and "< HTTP/1.1 200" in sh(f"harbor replay {first}")[1] and b4.cookie(DASH_HOST, "session") == first,
      (r.status_code, text_of(r.text)[:200]))
r = logout(b4)
check("4 log out: back to the sign-in page, and the cookie cleared",
      r.status_code == 303 and r.headers.get("location") == "/login" and r.headers.get("set-cookie", "").startswith("session=; Max-Age=0")
      and b4.cookie(DASH_HOST, "session") is None, (r.status_code, r.headers.get("set-cookie")))
out, err = sh(f"harbor replay {first}")
check("4 the old session ID replayed after logout: 401", "< HTTP/1.1 401" in err and "no valid session" in out, err + out)
check("4 ... with WWW-Authenticate: Cookie, naming the sign-in form and its cookie",
      '< Www-Authenticate: Cookie realm="Harbor dashboard", form-action="/login", cookie-name="session"' in err, err)
_, second = password_sign_in(b4)
check("4 signing in again makes a new session ID", second and second != first, (first, second))
out_new, err_new = sh(f"harbor replay {second}")
out_old, err_old = sh(f"harbor replay {first}")
check("4 the new ID works, and the old one stays dead", "< HTTP/1.1 200" in err_new and "< HTTP/1.1 401" in err_old, err_new + err_old)
out, err = sh("harbor replay -kq3NotARealSessionId")
check("4 an ID that starts with a dash still goes to the dashboard (401 for this made-up one), not to argparse",
      "> Cookie: session=-kq3NotARealSessionId" in err and "< HTTP/1.1 401" in err, err + out)
_, hint = sh("harbor lab session-ttl 3")
short_browser = Browser()
_, short_lived = password_sign_in(short_browser)
alive = sh(f"harbor replay {short_lived}")[1]
time.sleep(4)
dead = sh(f"harbor replay {short_lived}")[1]
check("4 extra: a short session ends on its own (3 s here; the mission uses a minute)",
      "< HTTP/1.1 200" in alive and "< HTTP/1.1 401" in dead and "The next sign-in's session lasts 3 s" in hint,
      hint + alive + dead)
password_sign_in(short_browser)
lasts = short_browser.get(f"{DASHBOARD}/lab/session").json().get("expires_in_seconds", 0)
check("4 extra: ... for that one sign-in: the next session lasts 30 minutes again", 1790 <= lasts <= 1800, lasts)


mission("Mission 7: the partner connects")
sh("harbor api-check introspect")  # as a learner may have left it after mission 6's extra
_, err = sh("harbor partner disconnect")  # a lab used before: no grant left, so Harbor Sign-in asks for consent as on a first visit
check("7 harbor partner disconnect warns when mission 6's introspection is still on", "harbor api-check local" in err, err)
sh("harbor api-check local")
p = Browser()
params, seen, r = connect_partner(p)
check("7 Connect Harbor shows the request: client_id, redirect_uri, scope=status:read, state, code_challenge, S256",
      params.get("client_id") == "partner-reports" and params.get("redirect_uri") == f"{PARTNER}/callback"
      and params.get("scope") == "status:read" and len(params.get("state", "")) >= 16 and len(params.get("code_challenge", "")) == 43
      and params.get("code_challenge_method") == "S256" and params.get("_continue", "").startswith(AUTHORIZE + "?"), params)
check("7 the request carries no verifier and no client secret", "code_verifier" not in params and "partner-lab-secret" not in params.get("_continue", ""))
check("7 the password is typed only on Harbor Sign-in", seen[:1] == ["password form at login.harbor.localhost"], seen)
check("7 Harbor Sign-in asks for consent: Read tracking status",
      any(s.startswith("consent") and "Read tracking status" in s and "Partner Reports" in s for s in seen), seen)
back = parse_qs(urlparse(params.get("_back", "")).query)
check("7 the browser comes back with a code in the address, and no token",
      back.get("code") and back.get("state", [""])[0] == params.get("state") and not any("token" in k for k in back), back)
exchange = {}
if r is not None and "<pre id=exchange>" in r.text:
    exchange = json.loads(unescape(re.search(r"<pre id=exchange>(.*?)</pre>", r.text, re.S).group(1)))
check("7 the backend's exchange: its client authentication, the code and the code_verifier; tokens back",
      exchange.get("client_authentication", "").startswith("Basic partner-reports:") and exchange["form"]["grant_type"] == "authorization_code"
      and exchange["form"].get("code_verifier") and exchange["answer"]["status"] == 200
      and {"access_token", "refresh_token"} <= set(exchange["answer"]), exchange)
check("7 the report: Healthy", r is not None and HEALTHY in r.text, text_of(r.text)[:300] if r is not None else None)
tokens = json.loads(sh("harbor partner tokens")[0])
claims = tokens.get("access_token_claims", {})
check("7 the partner's access token: Maya's, for the Status API, status:read, given to partner-reports",
      claims.get("sub") == "maya-01" and claims.get("aud") == "harbor-status-api" and claims.get("scope") == "status:read"
      and claims.get("azp") == "partner-reports", claims)
through_gateway = httpx.get(f"{PARTNER}/lab/tokens", headers=ADMIN, timeout=10).json()
check("7 the token view: whole values only for the toolbox's direct call; through the gateway, shortened even with the "
      "lab header", tokens.get("access_token", "").count(".") == 2 and through_gateway.get("access_token", "").endswith("…")
      and len(through_gateway["access_token"]) == 13, (tokens.get("lab_only"), through_gateway.get("access_token")))
r = p.post(f"{PARTNER}/refresh")
check("7 the refresh token works at Harbor Sign-in: a new access token", r.status_code == 200 and "id=refreshed" in r.text, text_of(r.text)[:300])
r = p.post(f"{PARTNER}/lab/refresh-token-to-api")
check("7 the refresh token at the Status API: 401", "The Status API answered 401" in r.text, text_of(r.text)[:300])
out, _ = sh("harbor partner disconnect")
check("7 Harbor disconnects the partner: Maya's grant removed", "grant removed" in out, out)
r = p.post(f"{PARTNER}/refresh")
check("7 after the disconnect, refreshing is refused", r.status_code == 400 and "Refresh refused" in r.text and "invalid_grant" in r.text,
      text_of(r.text)[:300])
r = p.get(f"{PARTNER}/")
check("7 ... while the access token still works until it expires", HEALTHY in r.text, text_of(r.text)[:300])
check("7 harbor partner wrong-verifier needs on or off (it never switches on by itself)",
      "on|off" in sh("harbor partner wrong-verifier")[1])
sh("harbor partner wrong-verifier on")
params, seen, r = connect_partner(p)
check("7 connecting again after the disconnect: no password (Maya is signed in), consent asked again",
      [s.split(":")[0] for s in seen] == ["consent"], seen)
check("7 extra: a wrong verifier: invalid_grant", r is not None and r.status_code == 400 and "invalid_grant" in r.text,
      text_of(r.text)[:400] if r is not None else seen)
params, seen, r = connect_partner(p)
check("7 extra: ... for one connection only: the next one (consent already given) comes straight back, connected",
      seen == [] and r is not None and HEALTHY in r.text, (seen, text_of(r.text)[:300] if r is not None else None))
first_access = json.loads(sh("harbor partner tokens")[0]).get("access_token", "")
sh("harbor api-check introspect")
out = curl(f'-H "Authorization: Bearer {first_access}" {API}')
sh("harbor api-check local")
check("7 extra: before the code is reused, Harbor Sign-in says the connection's access token is active (introspection)",
      status_of(out) == 200 and "Harbor Sign-in says it's still active" in header(out, "x-harbor-checked"), out)
reuse = json.loads(sh("harbor partner reuse-code")[0])
again = reuse.get("code_used_again", {})
check("7 extra (last): the code used again: invalid_grant", again.get("status") == 400 and again.get("error") == "invalid_grant", reuse)
check("7 extra: ... and Harbor Sign-in cancels what that code gave: the refresh token is refused",
      reuse.get("the_first_refresh_token_now_gets", "").startswith("400: invalid_grant"), reuse)
check("7 extra: ... while the Status API, checking locally, still accepts the access token until it expires",
      reuse.get("the_first_access_token_at_the_status_api") == f"200: {HEALTHY}"
      and "Harbor Sign-in says" not in reuse.get("what_the_status_api_checked", ""), reuse)
sh("harbor api-check introspect")
out = curl(f'-H "Authorization: Bearer {first_access}" {API}')
sh("harbor api-check local")
check("7 extra: ... and with introspection the same access token is refused at once",
      status_of(out) == 401 and body_of(out).get("reason") == "Harbor Sign-in says this token is no longer active", out)
check("7 a reload of the callback never sends the code to Harbor Sign-in again",
      "a code is used once" in p.get(f"{PARTNER}/callback?{urlparse(params['_back']).query}").text)


mission("Mission 8: company sign-in and one complete request")
_, hint = sh("harbor lab sign-in harbor")
check("8 harbor lab sign-in harbor says to log out first, and that Harbor Sign-in may not ask for the password",
      "Log out of the dashboard first" in hint and "single sign-on" in hint, hint)
d = Browser()
r = d.get(f"{DASHBOARD}/login")
check("8 the dashboard's sign-in page: Sign in with Harbor", "id=sign-in-with-harbor" in r.text and "id=password" not in r.text)
r = d.post(f"{DASHBOARD}/login", {"username": "maya", "password": "demo-only"})
check("8 the old password form is off too: Maya's right password sent to it gets 403 and no session",
      r.status_code == 403 and not r.headers.get_list("set-cookie") and "Harbor Sign-in handles the login" in text_of(r.text),
      (r.status_code, r.headers.get_list("set-cookie")))
learner = Browser()  # in order: the browser that signed in again in mission 4 and connected the partner in mission 7
learner.jar = {**b4.jar, **p.jar}
r = learner.get(f"{DASHBOARD}/")
still = "with a password" in r.text
r = logout(learner)
back, seen = through_harbor_sign_in(learner, learner.get(learner.get(f"{DASHBOARD}/auth/start").headers["location"]),
                                    f"{DASHBOARD}/auth/callback")
learner.get(back or f"{DASHBOARD}/auth/callback")
r = learner.get(f"{DASHBOARD}/")
check("8 in order, the browser from missions 4 and 7: signed in with the password until Log out; then Sign in with "
      "Harbor comes straight back (single sign-on: no password asked)",
      still and seen == [] and back and "with Harbor Sign-in" in r.text and HEALTHY in r.text, (still, seen, text_of(r.text)[:200]))
r = d.get(f"{DASHBOARD}/auth/start")
asked = parse_qs(urlparse(r.headers.get("location", "")).query)
check("8 the dashboard sends the browser to Harbor Sign-in: openid status:read, state, nonce, PKCE S256",
      r.status_code == 303 and r.headers["location"].startswith(AUTHORIZE + "?") and asked.get("client_id") == ["harbor-dashboard"]
      and asked.get("scope") == ["openid status:read"] and asked.get("state") and asked.get("nonce")
      and asked.get("code_challenge_method") == ["S256"], asked)
check("8 the attempt's cookie: short-lived, HttpOnly, only for /auth",
      re.fullmatch(r"login_attempt=[\w-]+; Secure; HttpOnly; SameSite=Lax; Path=/auth; Max-Age=300", r.headers.get("set-cookie", "")),
      r.headers.get("set-cookie"))
back, seen = through_harbor_sign_in(d, d.get(r.headers["location"]), f"{DASHBOARD}/auth/callback")
check("8 Harbor Sign-in asks for the password, and no consent for Harbor's own dashboard",
      seen == ["password form at login.harbor.localhost"], seen)
r = d.get(back or f"{DASHBOARD}/auth/callback")
check("8 back on the dashboard: a new session cookie, the attempt's cookie cleared",
      r.status_code == 303 and d.cookie(DASH_HOST, "session") and d.cookie(DASH_HOST, "login_attempt") is None, (r.status_code, d.jar))
sid = d.cookie(DASH_HOST, "session")
r = d.get(f"{DASHBOARD}/")
check("8 the dashboard: signed in with Harbor Sign-in, Healthy", "with Harbor Sign-in" in r.text and HEALTHY in r.text, text_of(r.text)[:300])
kept = d.get(f"{DASHBOARD}/lab/session").json().get("tokens_kept_with_the_session", {})
id_claims = kept.get("id_token", {}).get("claims") or {}
check("8 the session record holds the ID token: aud harbor-dashboard, with this sign-in's nonce",
      id_claims.get("aud") == "harbor-dashboard" and id_claims.get("sub") == "maya-01" and id_claims.get("nonce") == asked["nonce"][0],
      id_claims)
access_claims = kept.get("access_token", {}).get("claims") or {}
check("8 ... the access token: aud harbor-status-api, scope openid status:read (OpenID Connect adds openid)",
      access_claims.get("aud") == "harbor-status-api" and access_claims.get("scope") == "openid status:read", access_claims)
check("8 ... and the refresh token, which goes only to Harbor Sign-in", kept.get("refresh_token", {}).get("goes_only_to") == "Harbor Sign-in")
check("8 the browser holds only the session cookie for the dashboard", set(d.jar.get(DASH_HOST, {})) == {"session"}, d.jar.get(DASH_HOST))
shown = d.get(f"{DASHBOARD}/lab/session", headers=ADMIN).json().get("tokens_kept_with_the_session", {})
check("8 the session view through the gateway stays shortened, even with the lab header a page script could add",
      all(shown.get(name, {}).get("value", "").endswith("…") for name in ("id_token", "access_token", "refresh_token")), shown)
id_token = sh(f"harbor session {sid} --id-token")[0].strip()
out = curl(f'-H "Authorization: Bearer {id_token}" {API}')
check("8 the ID token sent to the Status API: 401 (audience)",
      status_of(out) == 401 and body_of(out).get("reason") == "the token was made for harbor-dashboard, not for harbor-status-api", out)
sh("harbor lab expire-access")
r = d.get(f"{DASHBOARD}/")
steps = d.get(f"{DASHBOARD}/lab/trace").json().get("steps", [])
trace = [f"{s['step']}: {s['detail']}" for s in steps]


def at(text: str) -> int:
    return next((i for i, line in enumerate(trace) if text in line), -1)


order = [at("Cookie: session="), at("found the session in the shared store"), at("grant_type=refresh_token"),
         at("a new access token, valid for 300 s"), at("Authorization: Bearer"),
         at("checked: JWT: signature (key "), at("200: Tracking service, Healthy"), at(f"dashboard -> browser: {HEALTHY}")]
check("8 the trace: cookie, session, refresh, Bearer, the API's checks, Healthy",
      HEALTHY in r.text and -1 not in order and order == sorted(order), "\n".join(trace))
check("8 ... the API's checks: signature, issuer, audience, expiry and scope",
      any(all(w in line for w in ("signature", "issuer", "audience", "expiry", "permission status:read: yes")) for line in trace),
      "\n".join(trace))


mission("Mission 9: retire the reporting job")
_, _, r = connect_partner(Browser())  # mission 7's last extra cancelled the partner's tokens: connect it again
check("9 the partner connected again", r is not None and HEALTHY in r.text)
rows = check_rows(sh("harbor check")[0])
check("9 all three callers work: the job, the dashboard, the partner",
      rows.get("reporting job (its API key)", ("",))[0] == "200" and rows.get("partner (its access token)", ("",))[0] == "200"
      and any(k.startswith("dashboard") and v[0] == "200" for k, v in rows.items()), rows)
sh("harbor key revoke")
rows = check_rows(sh("harbor check")[0])
dashboard_rows = [v for k, v in rows.items() if k.startswith("dashboard")]
check("9 only the job stopped, at once: 401 for the job, 200 for the dashboard and the partner",
      rows.get("reporting job (its API key)") == ("401", "this API key was revoked")
      and rows.get("partner (its access token)", ("",))[0] == "200" and dashboard_rows and all(v[0] == "200" for v in dashboard_rows), rows)
store = valkey.Valkey(host="valkey", port=6379, decode_responses=True)
record = json.loads(store.get(f"session:{sid}"))
record.update(refresh_token="spoiled-by-the-test", access_expires=0)  # as if Maya were disabled in Harbor Sign-in
store.set(f"session:{sid}", json.dumps(record), keepttl=True)
spoiled = check_rows(sh("harbor check")[0]).get(f"dashboard (maya's session {short(sid)})")
store.delete(f"session:{sid}")
check("9 a dashboard session whose refresh Harbor Sign-in refuses shows '-': no request reached the Status API",
      spoiled is not None and spoiled[0] == "-" and "refused to refresh" in spoiled[1], spoiled)


if SLOW:
    mission("Mission 6, the slow part: the revoked JWT at its exp")
    wait = fresh_claims["exp"] - time.time() + 2
    print(f"      waiting {max(wait, 0):.0f} s for the revoked token's exp", flush=True)
    time.sleep(max(wait, 0))
    out = curl(f'-H "Authorization: Bearer {fresh}" {API}')
    check("6 the revoked JWT after its exp: 401", status_of(out) == 401 and body_of(out).get("reason") == "the token has expired", out)

the_end()
summary()
sys.exit(1 if FAILED else 0)
