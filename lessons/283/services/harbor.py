#!/usr/bin/env python3
"""harbor: the exercise's helper commands, run in the toolbox (`docker compose exec toolbox bash`, then `harbor ...`).

`harbor job` sends the reporting job's own request and prints it the way it travels, with the answer. The others make
a token prepared for the example, decode or edit one, show what the Status API received, or show and rotate the job's
key, and say what they did. Explanations go to stderr, so `TOKEN=$(harbor token)` keeps only the token. Lab values only.
"""
import argparse
import base64
import json
import os
import sys
import time
import uuid
from urllib.parse import urlencode

import httpx
import jwt

from common import ISSUER, LAB_ADMIN, STATUS_API, b64url

ADMIN = {"X-Lab-Admin": LAB_ADMIN}
KEYS = "/lab-keys"


def say(text: str = ""):
    """Explanations go to stderr, so `TOKEN=$(harbor token)` captures only the token."""
    print(text, file=sys.stderr, flush=True)


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


# ---- the reporting job's key -----------------------------------------------------------------------------------------

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
    else:
        say("Rotating the job's key: a new key for the job, then the old one is revoked.")
        print(json.dumps(httpx.post(f"{STATUS_API}/lab/keys/rotate", headers=ADMIN, timeout=10).json(), indent=2,
                         ensure_ascii=False))


# ---- tokens --------------------------------------------------------------------------------------------------------

def prepared_jwt(audience: str, scope: str, issued: int, lifetime: int = 300) -> str:
    """A token prepared for the example: Harbor Sign-in's claims, signed with Harbor Sign-in's own (lab) key."""
    with open(f"{KEYS}/signing-key.pem", "rb") as f:
        private_key = f.read()
    with open(f"{KEYS}/jwks.json") as f:
        key_id = json.load(f)["keys"][0]["kid"]
    claims = {"exp": issued + lifetime, "iat": issued, "jti": str(uuid.uuid4()), "iss": ISSUER, "aud": audience,
              "sub": "maya-01", "typ": "Bearer", "azp": "harbor-dashboard", "scope": scope}
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": key_id})


def cmd_token(args):
    now = int(time.time())
    if args.opaque:
        say("The dashboard backend's opaque token, prepared for the example.")
        print(os.environ["DASHBOARD_API_TOKEN"])
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


def cmd_requests(args):
    for entry in httpx.get(f"{STATUS_API}/lab/requests", timeout=10).json()[: args.count]:
        print(json.dumps(entry, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(prog="harbor", description="The Harbor exercise's helper commands.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("job", help="the reporting job's request, with its API key")
    p.add_argument("--change", action="store_true", help="ask to change a setting instead of reading the status")
    p.add_argument("--key", help="send this key instead of the job's own")
    p.set_defaults(run=cmd_job)
    p = sub.add_parser("key", help="the job's key: show or rotate")
    p.add_argument("action", choices=["show", "rotate"])
    p.set_defaults(run=cmd_key)
    p = sub.add_parser("token", help="a token prepared for the example: a JWT for the Status API, or --opaque, --other-api, --expired")
    g = p.add_mutually_exclusive_group()
    for flag in ("--opaque", "--other-api", "--expired"):
        g.add_argument(flag, action="store_true")
    p.set_defaults(run=cmd_token)
    p = sub.add_parser("jwt", help="decode a JWT, or edit its payload and keep the old signature")
    p.add_argument("action", choices=["decode", "edit"])
    p.add_argument("token")
    p.add_argument("changes", nargs="*", help='for edit: claim=value, for example scope="status:read settings:write"')
    p.set_defaults(run=cmd_jwt)
    p = sub.add_parser("requests", help="the last requests the Status API received")
    p.add_argument("count", nargs="?", type=int, default=5)
    p.set_defaults(run=cmd_requests)
    args = parser.parse_args()
    if getattr(args, "action", None) == "edit" and not args.changes:
        parser.error("jwt edit needs at least one claim=value")
    try:
        args.run(args)
    except httpx.HTTPError as error:
        sys.exit(f"harbor: {type(error).__name__}: {error} (is the exercise running? docker compose ps)")


if __name__ == "__main__":
    main()
