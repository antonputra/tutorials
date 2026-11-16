#!/usr/bin/env python3
"""Every step of the exercise, typed as README.md types it, against the running exercise.

    docker compose --profile tests run --rm tests

It runs where the toolbox runs (the gateway's network) and checks what each command prints. Prints PASS or FAIL for
every check and exits 1 if any failed. Lab values only.
"""
import json
import re
import subprocess
import sys

API = "http://api.harbor.localhost:8080/api/status/tracking"
SETTINGS = "http://api.harbor.localhost:8080/api/settings/tracking"
FAILED: list[str] = []
COUNT = 0


def check(name: str, ok, detail=""):
    global COUNT
    COUNT += 1
    print(f"{'PASS' if ok else 'FAIL'}  {name}", flush=True)
    if not ok:
        FAILED.append(name)
        print("      " + str(detail)[:1500].replace("\n", "\n      "), flush=True)


def sh(command: str) -> tuple[str, str]:
    """A line typed in the toolbox: (stdout, stderr)."""
    done = subprocess.run(["bash", "-c", command], capture_output=True, text=True, timeout=60)
    return done.stdout.replace("\r\n", "\n"), done.stderr.replace("\r\n", "\n")


def status_of(text: str) -> int:
    found = re.search(r"HTTP/[\d.]+ (\d{3})", text)
    return int(found.group(1)) if found else 0


def header(text: str, name: str) -> str:
    found = re.search(rf"(?im)^<? ?{re.escape(name)}: (.*)$", text)
    return found.group(1).strip() if found else ""


def reason(text: str) -> str:
    found = re.search(r'\{"error":.*\}', text)
    return json.loads(found.group(0)).get("reason", "") if found else ""


print("== 2. The first private request")
out, _ = sh(f"curl -i {API}")
check("no credentials: 401 with WWW-Authenticate: Basic", status_of(out) == 401
      and header(out, "www-authenticate") == 'Basic realm="Harbor"', out)
out, _ = sh(f"curl -i -u maya:demo-only {API}")
check("Maya's username and password: 200 and Healthy", status_of(out) == 200 and '"status":"Healthy"' in out, out)
out, _ = sh(f"curl -sv -u maya:demo-only -o /dev/null {API} 2>&1 | grep Authorization")
check("curl -v shows the header it sent: Authorization: Basic bWF5YTpkZW1vLW9ubHk=",
      "Authorization: Basic bWF5YTpkZW1vLW9ubHk=" in out, out)
out, _ = sh("echo bWF5YTpkZW1vLW9ubHk= | base64 -d; echo")
check("the value decodes to maya:demo-only", out.strip() == "maya:demo-only", out)
out, _ = sh(f"curl -i -u maya:wrong {API}")
check("a wrong password: 401, wrong username or password", status_of(out) == 401
      and reason(out) == "wrong username or password", out)

print("\n== 3. The reporting job's own key")
out, err = sh("harbor job")
check("harbor job: the request with X-API-Key, then 200", "> X-API-Key: job_demo_" in err
      and status_of(err) == 200 and "Healthy" in out, err + out)
out, err = sh("harbor job --change")
check("harbor job --change: 403 Forbidden, the job may not change the settings", status_of(err) == 403
      and reason(out) == "reporting job may not change the tracking service's settings", err + out)
out, err = sh("harbor job --key job_demo_madeup")
check("a made-up key: 401, unknown API key", status_of(err) == 401 and reason(out) == "unknown API key", err + out)
out, _ = sh("harbor key show")
keys = json.loads(out)
active = [key for key in keys if key["active"]]  # one key, or after an earlier run's rotation, revoked ones as well
check("harbor key show: the job's key, status:read only", len(active) == 1 and active[0]["permissions"] == ["status:read"]
      and all(key["owner"] == "reporting job" for key in keys), out)

print("\n== 4. Bearer tokens")
out, _ = sh(f'curl -i -H "Authorization: Bearer $(harbor token --opaque)" {API}')
check("the opaque token: 200, the API looked it up", status_of(out) == 200
      and header(out, "x-harbor-checked").startswith("opaque token: looked up, active"), out)
token, _ = sh("harbor token")
token = token.strip()
out, err = sh(f'harbor jwt decode "{token}"')
payload = json.loads(out.split("payload:", 1)[1].split("\niat:", 1)[0])
check("harbor jwt decode: iss, sub, aud, exp and scope are readable", payload["iss"].endswith("/realms/harbor")
      and payload["sub"] == "maya-01" and payload["aud"] == "harbor-status-api" and payload["scope"] == "status:read"
      and payload["exp"] - payload["iat"] == 300 and "Decoded, not verified" in err, out + err)
out, _ = sh(f'curl -i -H "Authorization: Bearer {token}" {API}')
check("the JWT: 200, checked locally (signature, issuer, audience, expiry)", status_of(out) == 200
      and header(out, "x-harbor-checked").startswith("JWT: signature (key ")
      and "issuer, audience, expiry" in header(out, "x-harbor-checked"), out)

print("\n== 5. Tokens that should fail")
out, _ = sh(f'TOKEN="{token}"; BAD=$(harbor jwt edit "$TOKEN" scope="status:read settings:write"); '
            f'curl -i -X PUT -H "Authorization: Bearer $BAD" {SETTINGS}')
check("more scope, the old signature: 401, the signature doesn't match", status_of(out) == 401
      and reason(out) == "the signature doesn't match the token's content"
      and header(out, "www-authenticate") == 'Bearer realm="Harbor", error="invalid_token"', out)
out, _ = sh(f'curl -i -H "Authorization: Bearer $(harbor token --other-api)" {API}')
check("a token for another API: 401, made for harbor-billing-api", status_of(out) == 401
      and reason(out) == "the token was made for harbor-billing-api, not for harbor-status-api", out)
out, _ = sh(f'curl -i -H "Authorization: Bearer $(harbor token --expired)" {API}')
check("an expired token: 401, the token has expired", status_of(out) == 401 and reason(out) == "the token has expired", out)

print("\n== The extra: rotate the job's key")
out, _ = sh("harbor key rotate")
rotated = json.loads(out)
out, err = sh("harbor job")
check("after the rotation the job's new key works: 200", status_of(err) == 200 and rotated["new_key"] in err, err)
out, err = sh("harbor job --key job_demo_4Kx9Qe2mVt7Lp1Zr8Ws3")
check("the old key: 401, this API key was revoked", status_of(err) == 401 and reason(out) == "this API key was revoked",
      err + out)

print("\n== Harbor Sign-in's keys")
out, _ = sh("curl -si http://login.harbor.localhost:8080/realms/harbor/protocol/openid-connect/certs")
check("the published key set: one RSA key, public parts only", status_of(out) == 200
      and '"kty": "RSA"' in out and '"d"' not in out, out[:400])
out, _ = sh("curl -si http://login.harbor.localhost:8080/signing-key.pem; curl -si http://login.harbor.localhost:8080/realms/harbor/")
check("nothing else is published at Harbor Sign-in's address", out.count("HTTP/1.1 404") == 2 and "PRIVATE KEY" not in out, out)

print(f"\n{COUNT - len(FAILED)} of {COUNT} checks passed" + (f"; failed: {', '.join(FAILED)}" if FAILED else ""))
print("The checks rotated the job's key: before you do the exercise yourself, start from nothing "
      "(docker compose down -v, then docker compose up -d --wait).")
sys.exit(1 if FAILED else 0)
