"""Harbor's Status API: one private record, GET /api/status/tracking, and the checks in front of it.

Four kinds of caller, each with its own credential: Maya with Basic (script section 02), the reporting job with its
API key (04), the dashboard backend with an opaque Bearer token (05), and anyone holding an access token (a JWT)
from Harbor Sign-in (06-09). Lab code: the records live in memory and reset when the container restarts.
"""
import base64
import os
import secrets
import time
from collections import deque

import httpx
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from common import CERTS, INTROSPECT, ISSUER, LAB_ADMIN, short

AUDIENCE = "harbor-status-api"
STATUS = {"service": "Tracking service", "status": "Healthy"}

class JSONLine(JSONResponse):
    """JSON with a newline at the end, so the shell's prompt starts on its own line after curl prints an answer."""

    def render(self, content) -> bytes:
        return super().render(content) + b"\n"


app = FastAPI(title="Harbor Status API", default_response_class=JSONLine)
hasher = PasswordHasher()

# Section 02: Harbor keeps a password hash, never the password itself.
USERS = {"maya": {"password_hash": hasher.hash("demo-only"), "permissions": {"status:read"}}}
NOBODY = hasher.hash("an unknown user takes as long to refuse as a wrong password")

# Section 04: the reporting job's own credential record.
API_KEYS = {os.environ["JOB_API_KEY"]: {"owner": "reporting job", "permissions": {"status:read"}, "active": True}}

# Section 05: the dashboard backend's opaque token, prepared for the example.
OPAQUE_TOKENS = {os.environ["DASHBOARD_API_TOKEN"]: {"owner": "dashboard backend", "permissions": {"status:read"}, "active": True}}

# Section 06: Harbor Sign-in's published public keys, fetched once and cached.
JWKS = jwt.PyJWKClient(CERTS)
LAB = {"jwt_check": "local"}  # "introspect" also asks Harbor Sign-in about every token: the extra check
REQUESTS = deque(maxlen=50)


class Refused(Exception):
    def __init__(self, reason: str, challenge: str | None = None):
        super().__init__(reason)
        self.reason, self.challenge = reason, challenge


# Every 401 names how to authenticate (RFC 9110, 15.5.2). Basic and Bearer are registered schemes; API keys have none,
# so the job's challenge is Harbor's own and names the header the key goes in.
BEARER = 'Bearer realm="Harbor", error="invalid_token"'
API_KEY = 'ApiKey realm="Harbor", header="X-API-Key"'


def authenticate(request: Request):
    """Authentication: who is calling? Returns (caller, permissions, what was checked), or raises Refused (401)."""
    key = request.headers.get("x-api-key")
    if key is not None:
        record = API_KEYS.get(key)
        if record is None:
            raise Refused("unknown API key", API_KEY)
        if not record["active"]:
            raise Refused("this API key was revoked", API_KEY)
        return record["owner"], record["permissions"], "API key: looked up, active"

    scheme, _, value = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() == "basic":
        try:
            username, _, password = base64.b64decode(value, validate=True).decode().partition(":")
        except ValueError:
            raise Refused("that Basic value isn't Base64 of username:password", 'Basic realm="Harbor"')
        user = USERS.get(username)
        started = time.perf_counter()
        try:
            hasher.verify(user["password_hash"] if user else NOBODY, password)
        except VerificationError:
            raise Refused("wrong username or password", 'Basic realm="Harbor"')
        if user is None:
            raise Refused("wrong username or password", 'Basic realm="Harbor"')
        took = (time.perf_counter() - started) * 1000
        return username, user["permissions"], f"Basic: password checked against the stored hash in {took:.0f} ms"

    if scheme.lower() == "bearer":
        token = value.strip()
        record = OPAQUE_TOKENS.get(token)
        if record is not None:
            if not record["active"]:
                raise Refused("this token was revoked", BEARER)
            return record["owner"], record["permissions"], "opaque token: looked up, active"
        return check_jwt(token)

    raise Refused("no credentials", 'Basic realm="Harbor"')


def check_jwt(token: str):
    """Section 06: verify locally, with Harbor's expected algorithm and trusted key, then the claims."""
    try:
        signing_key = JWKS.get_signing_key_from_jwt(token)
    except jwt.exceptions.PyJWKClientConnectionError:
        raise Refused("Harbor Sign-in's published keys couldn't be fetched", BEARER)
    except jwt.exceptions.PyJWKClientError:
        raise Refused("signed with a key Harbor Sign-in doesn't publish", BEARER)
    except jwt.exceptions.DecodeError:
        raise Refused("not a token this API knows", BEARER)
    try:  # the expiry is checked last, below, so a token made for another API always says so
        claims = jwt.decode(token, signing_key.key, algorithms=["RS256"], audience=AUDIENCE, issuer=ISSUER,
                            options={"require": ["exp", "iss", "aud", "sub"], "verify_exp": False})
    except jwt.exceptions.InvalidSignatureError:
        raise Refused("the signature doesn't match the token's content", BEARER)
    except jwt.exceptions.InvalidAudienceError:
        intended = jwt.decode(token, options={"verify_signature": False}).get("aud")
        raise Refused(f"the token was made for {intended}, not for {AUDIENCE}", BEARER)
    except jwt.exceptions.InvalidIssuerError:
        raise Refused("the token comes from another issuer", BEARER)
    except jwt.exceptions.InvalidTokenError as error:
        raise Refused(f"invalid token: {error}", BEARER)
    if not isinstance(claims["exp"], int) or claims["exp"] <= time.time():
        raise Refused("the token has expired", BEARER)
    checked = f"JWT: signature (key {signing_key.key_id[:8]}...), issuer, audience, expiry (in {int(claims['exp'] - time.time())} s)"
    if LAB["jwt_check"] == "introspect":
        answer = httpx.post(INTROSPECT, data={"token": token},
                            auth=("harbor-status-api", os.environ["STATUS_API_SECRET"]), timeout=10).json()
        if not answer.get("active"):
            raise Refused("Harbor Sign-in says this token is no longer active", BEARER)
        checked += ", and Harbor Sign-in says it's still active"
    return claims["sub"], set(claims.get("scope", "").split()), checked


def answer(request: Request, status: int, body: dict, caller=None, checked=None, challenge=None):
    REQUESTS.appendleft({
        "time": time.strftime("%H:%M:%S UTC", time.gmtime()), "method": request.method, "path": request.url.path,
        "authorization": request.headers.get("authorization"), "x-api-key": request.headers.get("x-api-key"),
        "status": status, "caller": caller, "checked": checked, "reason": body.get("reason"),
    })
    headers = {"WWW-Authenticate": challenge} if challenge else {}
    if checked:
        headers["X-Harbor-Checked"] = checked
    return JSONLine(body, status_code=status, headers=headers)


def guarded(request: Request, permission: str, action: str):
    try:
        caller, permissions, checked = authenticate(request)
    except Refused as refused:  # 401: Harbor doesn't know who is asking
        return answer(request, 401, {"error": "unauthorized", "reason": refused.reason}, challenge=refused.challenge)
    if permission not in permissions:  # 403: Harbor knows exactly who is asking, and the answer is still no
        bearer = checked.startswith(("JWT", "opaque token"))  # a Bearer token names the scope it lacks (RFC 6750, 3.1)
        challenge = f'Bearer realm="Harbor", error="insufficient_scope", scope="{permission}"' if bearer else None
        return answer(request, 403, {"error": "forbidden", "reason": f"{caller} may not {action}"}, caller, checked,
                      challenge)
    return answer(request, 200, STATUS, caller, f"{checked}; permission {permission}: yes")


@app.get("/api/status/tracking")
def read_status(request: Request):
    return guarded(request, "status:read", "read the tracking status")


@app.put("/api/settings/tracking")
def change_settings(request: Request):
    return guarded(request, "settings:write", "change the tracking service's settings")


@app.get("/health")
def health():
    return {"ok": True}


# Lab only: what arrived, and the switches the toolbox uses. A real API has none of this.
def admin(request: Request):
    return request.headers.get("x-lab-admin") == LAB_ADMIN


@app.get("/lab/requests")
def lab_requests():
    return list(REQUESTS)


@app.get("/lab/keys")
def lab_keys(request: Request):
    full = admin(request)
    return [{"key": key if full else short(key, 12), **{k: sorted(v) if isinstance(v, set) else v for k, v in rec.items()}}
            for key, rec in API_KEYS.items()]


@app.post("/lab/keys/rotate")
def lab_rotate(request: Request):
    if not admin(request):
        return JSONLine({"error": "lab admin only"}, status_code=403)
    old = [k for k, r in API_KEYS.items() if r["active"]]
    new = "job_demo_" + secrets.token_urlsafe(18)
    API_KEYS[new] = {"owner": "reporting job", "permissions": {"status:read"}, "active": True}
    for key in old:
        API_KEYS[key]["active"] = False
    return {"new_key": new, "revoked": [short(k, 12) for k in old]}


@app.post("/lab/keys/revoke")
def lab_revoke(request: Request):
    if not admin(request):
        return JSONLine({"error": "lab admin only"}, status_code=403)
    revoked = [k for k, r in API_KEYS.items() if r["active"]]
    for key in revoked:
        API_KEYS[key]["active"] = False
    return {"revoked": [short(k, 12) for k in revoked]}


@app.get("/lab/jwt-check")
def lab_jwt_mode():
    return LAB


@app.post("/lab/jwt-check/{mode}")
def lab_jwt_check(mode: str, request: Request):
    if not admin(request) or mode not in ("local", "introspect"):
        return JSONLine({"error": "lab admin only; mode is local or introspect"}, status_code=403)
    LAB["jwt_check"] = mode
    return LAB
