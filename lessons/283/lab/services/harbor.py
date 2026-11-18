#!/usr/bin/env python3
"""harbor: the lab's helper commands, run in the toolbox (`docker compose exec toolbox harbor ...`).

The commands that send a mission's own requests (harbor job, harbor replay, harbor revoke) print each request the way
it travels, and the answer. `harbor token --fresh` prints each step of its sign-in. The others read the lab's teaching
views, change a lab switch or do lab plumbing, and say what they did. Explanations go to stderr. Lab values only.
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import uuid
from html import unescape
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import httpx
import jwt

from common import AUTHORIZE, DASHBOARD, ISSUER, LAB_ADMIN, PARTNER, REVOKE, STATUS_API, TOKEN, b64url, new_pkce

ADMIN = {"X-Lab-Admin": LAB_ADMIN}
KEYS = "/lab-keys"
SIGN_IN = ISSUER.split("/realms/")[0]
DASHBOARD_CLIENT = ("harbor-dashboard", os.environ.get("DASHBOARD_CLIENT_SECRET", "dashboard-lab-secret"))
# The services themselves, not through the gateway browsers use: the teaching views give whole token values only to
# these direct calls. The toolbox shares the gateway's network, so the names resolve here.
DASHBOARD_SERVER = "http://dashboard-a:8000"
PARTNER_SERVER = "http://partner:8000"


def say(text: str = ""):
    """Explanations go to stderr, so `TOKEN=$(harbor token)` captures only the token."""
    print(text, file=sys.stderr, flush=True)


def clip(text: str, keep: int = 110) -> str:
    return text if len(text) <= keep else text[:keep] + "…"


def send(method: str, url: str, headers: dict | None = None, data: dict | None = None, quiet: bool = False) -> httpx.Response:
    """Send one request and print it the way it travels: the request line, the headers, the body, then the answer."""
    request = httpx.Request(method, url, headers=headers or {}, data=data)
    if not quiet:
        say(f"> {method} {request.url.raw_path.decode()} HTTP/1.1")
        say(f"> Host: {request.url.netloc.decode()}")
        for name, value in (headers or {}).items():
            say(f"> {name}: {value}")
        if data:
            say(f"> Content-Type: application/x-www-form-urlencoded")
            say(">")
            say(f"> {urlencode(data)}")
        say()
    response = httpx.Client(timeout=15).send(request)
    if not quiet:
        say(f"< HTTP/1.1 {response.status_code} {response.reason_phrase}")
        for name in ("www-authenticate", "x-harbor-checked", "location", "set-cookie"):
            for value in response.headers.get_list(name):
                say(f"< {name.title()}: {value}")
        text = response.text.rstrip("\n")  # the APIs end their JSON with a newline; print adds its own
        print(text if len(text) < 2000 else text[:2000] + " ...", flush=True)
    return response


# ---- the reporting job (section 04) ---------------------------------------------------------------------------------

def job_key() -> str:
    keys = httpx.get(f"{STATUS_API}/lab/keys", headers=ADMIN, timeout=10).json()
    return keys[-1]["key"]  # the job uses its newest key, even after it was revoked


def cmd_job(args):
    key = args.key or job_key()
    if args.change:
        send("PUT", f"{STATUS_API}/api/settings/tracking", {"X-API-Key": key})
    else:
        send("GET", f"{STATUS_API}/api/status/tracking", {"X-API-Key": key})


def cmd_key(args):
    if args.action == "show":
        print(json.dumps(httpx.get(f"{STATUS_API}/lab/keys", headers=ADMIN, timeout=10).json(), indent=2,
                         ensure_ascii=False))
    elif args.action == "rotate":
        say("Rotating the job's key: a new key for the job, then the old one is revoked.")
        print(json.dumps(httpx.post(f"{STATUS_API}/lab/keys/rotate", headers=ADMIN, timeout=10).json(), indent=2,
                         ensure_ascii=False))
    else:
        say("Revoking the job's key in its credential record.")
        print(json.dumps(httpx.post(f"{STATUS_API}/lab/keys/revoke", headers=ADMIN, timeout=10).json(), indent=2,
                         ensure_ascii=False))


# ---- tokens (sections 05 and 06) -------------------------------------------------------------------------------------

def prepared_jwt(audience: str, scope: str, issued: int, lifetime: int = 300) -> str:
    """A token prepared for the example: Harbor Sign-in's claims, signed with Harbor Sign-in's own (lab) key."""
    with open(f"{KEYS}/signing-key.pem", "rb") as f:
        private_key = f.read()
    with open(f"{KEYS}/jwks.json") as f:
        key_id = json.load(f)["keys"][0]["kid"]
    claims = {"exp": issued + lifetime, "iat": issued, "jti": str(uuid.uuid4()), "iss": ISSUER, "aud": audience,
              "sub": "maya-01", "typ": "Bearer", "azp": "harbor-dashboard", "scope": scope}
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": key_id})


class Browser:
    """Just enough browser for Harbor Sign-in's form: keeps each host's cookies, Secure ones too (*.localhost is a
    secure context in a browser, while Python's cookie jar would hold them back over http), follows nothing, and prints
    each request and its answer on stderr."""

    def __init__(self):
        self.jar: dict[str, dict] = {}
        self.http = httpx.Client(timeout=15, follow_redirects=False)

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        host = urlparse(url).hostname
        cookies = self.jar.get(host, {})
        headers = {"Cookie": "; ".join(f"{k}={v}" for k, v in cookies.items())} if cookies else {}
        say(f"> {method} {clip(url)}" + (f"  (form: {urlencode(kwargs['data'])})" if kwargs.get("data") else ""))
        response = self.http.request(method, url, headers=headers, **kwargs)
        location = response.headers.get("location")
        say(f"< {response.status_code} {response.reason_phrase}" + (f", Location: {clip(location)}" if location else ""))
        for line in response.headers.get_list("set-cookie"):
            name, _, value = line.split(";", 1)[0].partition("=")
            if re.search(r"max-age=0\b|expires=thu, 01[- ]jan[- ]1970", line, re.I):
                self.jar.setdefault(host, {}).pop(name.strip(), None)
            else:
                self.jar.setdefault(host, {})[name.strip()] = value.strip()
        self.http.cookies.clear()
        return response


def fresh_token() -> str:
    """Sign in as Maya on Harbor Sign-in, the way the dashboard does (authorization code + PKCE), and keep the access
    token. Scripted for the lab: it fills in Harbor Sign-in's form like a browser would. Never the password grant."""
    verifier, challenge = new_pkce()
    client_id, secret = DASHBOARD_CLIENT
    params = {"response_type": "code", "client_id": client_id, "redirect_uri": f"{DASHBOARD}/auth/callback",
              "scope": "status:read", "state": b64url(os.urandom(12)), "code_challenge": challenge,
              "code_challenge_method": "S256"}
    browser = Browser()
    response = browser.request("GET", AUTHORIZE + "?" + urlencode(params))
    for _ in range(5):
        if response.status_code in (302, 303) and response.headers["location"].startswith(f"{DASHBOARD}/auth/callback"):
            break
        if response.status_code in (302, 303):
            response = browser.request("GET", urljoin(str(response.url), response.headers["location"]))
            continue
        form = re.search(r'<form[^>]*\saction="([^"]+)"', response.text)
        if not form or 'name="password"' not in response.text:
            sys.exit(f"harbor: Harbor Sign-in's sign-in page didn't appear (status {response.status_code})")
        response = browser.request("POST", urljoin(str(response.url), unescape(form.group(1))),
                                   data={"username": "maya", "password": "demo-only", "credentialId": ""})
    else:
        sys.exit("harbor: no code came back from Harbor Sign-in")
    query = parse_qs(urlparse(response.headers["location"]).query)
    if query.get("state", [""])[0] != params["state"]:
        sys.exit("harbor: the state that came back doesn't match")
    say(f"> POST {TOKEN}  (form: grant_type=authorization_code, code={query['code'][0][:10]}…, "
        f"code_verifier={verifier[:8]}…; the dashboard's client ID and secret in Authorization: Basic)")
    tokens = httpx.post(TOKEN, data={"grant_type": "authorization_code", "code": query["code"][0],
                                     "redirect_uri": params["redirect_uri"], "code_verifier": verifier},
                        auth=(client_id, secret), timeout=15)
    say(f"< {tokens.status_code} {tokens.reason_phrase}")
    if tokens.status_code != 200:
        sys.exit(f"harbor: the code exchange failed: {tokens.text[:200]}")
    return tokens.json()["access_token"]


def cmd_token(args):
    now = int(time.time())
    if args.opaque:
        say("The dashboard backend's opaque token, prepared for the example.")
        print(os.environ["DASHBOARD_API_TOKEN"])
    elif args.fresh:
        say("Signing in as Maya on Harbor Sign-in with the dashboard's code flow, the way a browser would (lab helper):")
        token = fresh_token()
        if sys.stdout.isatty():  # not when the token goes into a variable: TOKEN=$(harbor token --fresh)
            say("The access token:")
        print(token)
    elif args.other_api:
        say("Prepared for the example, signed with Harbor Sign-in's key: a token made for another API (Harbor's billing API).")
        print(prepared_jwt("harbor-billing-api", "billing:read", now))
    elif args.expired:
        say("Prepared for the example, signed with Harbor Sign-in's key: a token that expired 5 minutes ago.")
        print(prepared_jwt("harbor-status-api", "status:read", now - 600))
    else:
        say("Prepared for the example, signed with Harbor Sign-in's key: an access token for the Status API, valid for 5 minutes.")
        print(prepared_jwt("harbor-status-api", "status:read", now))


def part(segment: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4)))


def cmd_jwt(args):
    pieces = args.token.strip().split(".")
    if len(pieces) != 3:
        sys.exit("harbor: a signed JWT has three parts separated by dots")
    if args.action == "decode":
        header, payload = part(pieces[0]), part(pieces[1])
        say("Decoded, not verified: anyone holding the token can read this.")
        print("header:", json.dumps(header, indent=2, ensure_ascii=False))
        print("payload:", json.dumps(payload, indent=2, ensure_ascii=False))
        for claim in ("iat", "exp"):
            if claim in payload:
                left = payload[claim] - int(time.time())
                when = f"in {left} s" if left > 0 else "now" if left == 0 else f"{-left} s ago"
                print(f"{claim}: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(payload[claim]))} ({when})")
        print(f"signature: {pieces[2][:16]}... ({len(base64.urlsafe_b64decode(pieces[2] + '=' * (-len(pieces[2]) % 4)))} bytes)")
    else:
        payload = part(pieces[1])
        for change in args.changes:
            name, _, value = change.partition("=")
            payload[name] = int(value) if value.isdigit() else value
        say(f"Changed {', '.join(c.partition('=')[0] for c in args.changes)} in the payload and kept the old signature.")
        print(".".join([pieces[0], b64url(json.dumps(payload, separators=(",", ":")).encode()), pieces[2]]))


def cmd_revoke(args):
    say("Revoking the token at Harbor Sign-in (RFC 7009), as the dashboard client that received it.")
    send("POST", REVOKE, {"Authorization": "Basic " + base64.b64encode(":".join(DASHBOARD_CLIENT).encode()).decode()},
         {"token": args.token.strip(), "token_type_hint": "access_token"})


def cmd_api_check(args):
    say(f"The Status API now checks JWTs {'locally only' if args.mode == 'local' else 'locally, then asks Harbor Sign-in about each one (introspection)'}.")
    print(json.dumps(httpx.post(f"{STATUS_API}/lab/jwt-check/{args.mode}", headers=ADMIN, timeout=10).json(),
                     ensure_ascii=False))
    if args.mode == "introspect":
        say("Switch back with `harbor api-check local` (or `harbor lab reset`) when you're done: the later missions "
            "expect local checks, and with introspection a disconnected partner's access token is refused at once.")


def cmd_requests(args):
    for entry in httpx.get(f"{STATUS_API}/lab/requests", timeout=10).json()[: args.count]:
        print(json.dumps(entry, ensure_ascii=False))


# ---- the dashboard (section 03) --------------------------------------------------------------------------------------

def cmd_replay(args):
    send("GET", f"{DASHBOARD}/status", {"Cookie": f"session={args.session_id.strip()}"})


def cmd_session(args):
    """Mission 8: Harbor's record for one dashboard session, with the whole token values (the lab's teaching view,
    asked of a dashboard server directly)."""
    answer = httpx.get(f"{DASHBOARD_SERVER}/lab/session",
                       headers={**ADMIN, "Cookie": f"session={args.session_id.strip()}"}, timeout=10)
    view = answer.json()
    if answer.status_code != 200:
        sys.exit("harbor: no valid session has this ID: it expired, was logged out, or the ID was mistyped "
                 "(copy it again from DevTools: Application, Cookies in Chrome and Edge; Storage, Cookies in Firefox)")
    if not (args.id_token or args.access_token):
        print(json.dumps(view, indent=2, ensure_ascii=False))
        return
    name = "id_token" if args.id_token else "access_token"
    token = view.get("tokens_kept_with_the_session", {}).get(name)
    if token is None:
        sys.exit("harbor: this session keeps no tokens: it was made by the password form. "
                 "Switch to Sign in with Harbor (harbor lab sign-in harbor), log out and sign in again.")
    label = "ID token" if name == "id_token" else "access token"
    say(f"The {label} kept with this session on the dashboard's server (the lab's teaching view; Maya's browser "
        "never had it).")
    expires = (token.get("claims") or {}).get("exp")
    if expires and expires <= time.time():
        ago = int(time.time() - expires)
        say(f"It expired {ago} s ago: an ID token lives 5 minutes, because the dashboard needs it only at sign-in."
            if name == "id_token" else
            f"It expired {ago} s ago: open the dashboard, and it gets a new one with the refresh token.")
    print(token["value"])


def cmd_lab(args):
    names = {"samesite": ("samesite", {"lax": "Lax", "none": "None", "strict": "Strict"}),
             "session-ttl": ("session_ttl", None), "sign-in": ("signin", {"password": "password", "harbor": "harbor"})}
    if args.setting == "reset":
        lab_reset()
        return
    if args.setting == "expire-access":
        print(json.dumps(httpx.post(f"{DASHBOARD}/lab/expire-access", headers=ADMIN, timeout=10).json(),
                         ensure_ascii=False))
        return
    key, values = names[args.setting]
    value = values.get(args.value.lower()) if values else args.value
    if value is None:
        sys.exit(f"harbor: {args.setting} is one of {', '.join(values)}")
    answer = httpx.post(f"{DASHBOARD}/lab/config", headers=ADMIN, json={key: value}, timeout=10)
    if answer.status_code != 200:
        sys.exit(f"harbor: {answer.json().get('error')} (session-ttl takes a number of seconds)")
    print(json.dumps(answer.json(), ensure_ascii=False))
    if args.setting == "samesite":
        say("The dashboard sets the new cookie at the next sign-in: log out, then sign in again. "
            "The starting value: harbor lab samesite lax")
    elif args.setting == "session-ttl":
        say(f"The next sign-in's session lasts {value} s; the sign-ins after it get the usual 30 minutes.")
    elif value == "harbor":
        say("The sign-in page now offers only Sign in with Harbor, and the password form is off. Log out of the "
            "dashboard first: a session made by the password form stays signed in. Harbor Sign-in may not ask for "
            "the password: if Maya signed in there in mission 7, that sign-in serves all of Harbor's apps (single "
            "sign-on). The starting value: harbor lab sign-in password")
    else:
        say("The password form is back: log out, then sign in again.")


def lab_reset():
    """Every switch back to its starting value, as on a fresh lab, and a working key for the reporting job."""
    for url in (f"{DASHBOARD}/lab/reset", f"{STATUS_API}/lab/jwt-check/local", f"{PARTNER}/lab/wrong-verifier/off"):
        httpx.post(url, headers=ADMIN, timeout=10).raise_for_status()
    say("Back to the starting values: the dashboard's password form, SameSite=Lax, 30-minute sessions, local JWT "
        "checks at the Status API, and the partner's right PKCE verifier.")
    if not any(key["active"] for key in httpx.get(f"{STATUS_API}/lab/keys", headers=ADMIN, timeout=10).json()):
        httpx.post(f"{STATUS_API}/lab/keys/rotate", headers=ADMIN, timeout=10).raise_for_status()
        say("The job's key was revoked (mission 9), so the job has a new one.")
    say("Sessions and connections stay as they are: log out of the dashboard to sign in again.")


# ---- the partner (section 07) ----------------------------------------------------------------------------------------

def keycloak_admin() -> dict:
    """Harbor's own administrator, in Harbor Sign-in's admin API (Keycloak's admin login, not one of Harbor's clients)."""
    answer = httpx.post(f"{SIGN_IN}/realms/master/protocol/openid-connect/token", timeout=15, data={
        "grant_type": "password", "client_id": "admin-cli", "username": "admin", "password": "admin"})
    return {"Authorization": f"Bearer {answer.json()['access_token']}"}


def cmd_partner(args):
    if args.action == "disconnect":
        say("Harbor disconnects the partner: Harbor Sign-in removes Maya's grant for Partner Reports. (Lab plumbing: "
            "through Harbor Sign-in's admin API, signed in with Keycloak's own admin login, admin / admin, which none "
            "of Harbor's clients uses.)")
        answer = httpx.delete(f"{SIGN_IN}/admin/realms/harbor/users/maya-01/consents/partner-reports",
                              headers=keycloak_admin(), timeout=15)
        print("grant removed" if answer.status_code == 204 else f"answer {answer.status_code}: {answer.text[:200]}")
        if httpx.get(f"{STATUS_API}/lab/jwt-check", timeout=10).json().get("jwt_check") == "introspect":
            say("Note: the Status API still asks Harbor Sign-in about every token (mission 6's extra), so the partner's "
                "access token stops working at once. For mission 7 as written: harbor api-check local")
    elif args.action == "reuse-code":
        say("The partner's backend sends its last code to Harbor Sign-in again, then tries what the first exchange gave.")
        print(json.dumps(httpx.post(f"{PARTNER}/lab/exchange-again", headers=ADMIN, timeout=15).json(), indent=2,
                         ensure_ascii=False))
    elif args.action == "wrong-verifier":
        if args.value not in ("on", "off"):
            sys.exit("harbor: partner wrong-verifier on|off")
        print(json.dumps(httpx.post(f"{PARTNER}/lab/wrong-verifier/{args.value}", headers=ADMIN, timeout=10).json(),
                         ensure_ascii=False))
        if args.value == "on":
            say("The partner's next connection sends a wrong PKCE verifier, once; the one after it is right again.")
    else:
        print(json.dumps(httpx.get(f"{PARTNER_SERVER}/lab/tokens", headers=ADMIN, timeout=10).json(), indent=2,
                         ensure_ascii=False))


# ---- mission 9: the three callers, right now ----------------------------------------------------------------------------

def cmd_check(args):
    say("Each caller sends GET /api/status/tracking now, with its own credential; the Status API's answers "
        "(- when no request reached it):")
    rows = []
    job = httpx.get(f"{STATUS_API}/api/status/tracking", headers={"X-API-Key": job_key()}, timeout=10)
    answer = job.json()
    rows.append(("reporting job (its API key)", job.status_code,
                 f"{answer['service']} — {answer['status']}" if job.status_code == 200 else answer.get("reason")))
    sessions = httpx.get(f"{DASHBOARD}/lab/check", headers=ADMIN, timeout=15).json()
    for s in sessions:
        rows.append((f"dashboard ({s['user']}'s session {s['session_id']})", s.get("status") or "-", s["text"]))
    if not sessions:
        rows.append(("dashboard", "-", "nobody is signed in to the dashboard"))
    partner = httpx.get(f"{PARTNER}/lab/check", headers=ADMIN, timeout=15).json()
    rows.append(("partner (its access token)", partner.get("status", "-"), partner.get("text")))
    for who, code, text in rows:
        print(f"{who:<44} {code!s:<4} {text}")


def session_id_last(argv: list[str]) -> list[str]:
    """`harbor replay ID` and `harbor session ID`: an ID that starts with "-" is still an ID, not an option."""
    if argv[:1] in (["replay"], ["session"]):
        flags = [a for a in argv[1:] if a in ("-h", "--help", "--id-token", "--access-token")]
        return argv[:1] + flags + ["--"] + [a for a in argv[1:] if a not in flags and a != "--"]
    return argv


def main():
    parser = argparse.ArgumentParser(prog="harbor", description="The Harbor lab's helper commands.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("job", help="the reporting job's request, with its API key")
    p.add_argument("--change", action="store_true", help="ask to change a setting instead of reading the status")
    p.add_argument("--key", help="send this key instead of the job's own")
    p.set_defaults(run=cmd_job)
    p = sub.add_parser("key", help="the job's key: show, rotate or revoke")
    p.add_argument("action", choices=["show", "rotate", "revoke"])
    p.set_defaults(run=cmd_key)
    p = sub.add_parser("token", help="a token prepared for the example (--fresh: a new one from Harbor Sign-in)")
    g = p.add_mutually_exclusive_group()
    for flag in ("--opaque", "--other-api", "--expired", "--fresh"):
        g.add_argument(flag, action="store_true")
    p.set_defaults(run=cmd_token)
    p = sub.add_parser("jwt", help="decode a JWT, or edit its payload and keep the old signature")
    p.add_argument("action", choices=["decode", "edit"])
    p.add_argument("token")
    p.add_argument("changes", nargs="*", help='for edit: claim=value, for example scope="status:read settings:write"')
    p.set_defaults(run=cmd_jwt)
    p = sub.add_parser("revoke", help="revoke a token at Harbor Sign-in")
    p.add_argument("token")
    p.set_defaults(run=cmd_revoke)
    p = sub.add_parser("api-check", help="how the Status API checks JWTs: local or introspect")
    p.add_argument("mode", choices=["local", "introspect"])
    p.set_defaults(run=cmd_api_check)
    p = sub.add_parser("requests", help="the last requests the Status API received")
    p.add_argument("count", nargs="?", type=int, default=5)
    p.set_defaults(run=cmd_requests)
    p = sub.add_parser("replay", help="ask the dashboard for the status with this session ID")
    p.add_argument("session_id")
    p.set_defaults(run=cmd_replay)
    p = sub.add_parser("session", help="the dashboard's record for this session ID (--id-token, --access-token: one value)")
    p.add_argument("session_id")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--id-token", action="store_true")
    g.add_argument("--access-token", action="store_true")
    p.set_defaults(run=cmd_session)
    p = sub.add_parser("lab", help="the lab's switches: samesite, session-ttl, sign-in, expire-access; reset: every "
                                   "switch back to its starting value")
    p.add_argument("setting", choices=["samesite", "session-ttl", "sign-in", "expire-access", "reset"])
    p.add_argument("value", nargs="?", default="")
    p.set_defaults(run=cmd_lab)
    p = sub.add_parser("partner", help="Harbor's side of the partner: disconnect, tokens, and mission 7's extras "
                                       "(wrong-verifier on|off, reuse-code)")
    p.add_argument("action", choices=["disconnect", "tokens", "reuse-code", "wrong-verifier"])
    p.add_argument("value", nargs="?", default="")
    p.set_defaults(run=cmd_partner)
    p = sub.add_parser("check", help="the three callers right now: the job, the dashboard, the partner")
    p.set_defaults(run=cmd_check)
    args = parser.parse_args(session_id_last(sys.argv[1:]))
    if getattr(args, "action", None) == "edit" and not args.changes:
        parser.error("jwt edit needs at least one claim=value")
    try:
        args.run(args)
    except httpx.HTTPError as error:
        sys.exit(f"harbor: {type(error).__name__}: {error} (is the lab running? docker compose ps)")


if __name__ == "__main__":
    main()
