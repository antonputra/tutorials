# The Harbor lab: Authentication Explained

The full lab for Anton Putra's video "Authentication Explained": nine missions, about 40 minutes, on your own computer.
Harbor is a fictional company with a Status API, a dashboard, a sign-in service and a partner that wants Harbor's data.
You sign in as Maya, send her requests yourself, and watch what each service checks. The missions are on the lab page,
`https://antonputra.com/labs/authentication/`; this folder is everything they run on. Short on time? The 10-minute
exercise is one folder up, in [../README.md](../README.md), with its page at
`https://antonputra.com/exercises/authentication-explained/`.

## Run it

You need Docker with Compose, about 2 GB of free disk, at least 2 GB of memory for Docker (the lab's containers use
about 1 GB), and port 8080 free on 127.0.0.1.
For the browser missions, use Chrome, Edge or Firefox: Safari refuses the lab's `Secure` cookies on `http://*.localhost`
addresses.

The lab is this folder of the tutorials repository, `https://github.com/antonputra/tutorials`. After you clone it (the
lab's page has the command):

```bash
cd tutorials/lessons/283/lab
docker compose up -d --wait          # start; returns once everything is ready, in about 20 s
docker compose exec toolbox bash     # the terminal the missions use: curl, jq, base64 and the harbor helpers
docker compose down -v               # stop and delete everything, the lab's signing key included
```

The first start also downloads about 400 MB of images and packages (about 1.5 GB on disk, most of it Keycloak) and
builds the lab's image: about a minute on a fast connection, a few minutes on a slower one.

| address | what it is |
|---|---|
| `http://dashboard.harbor.localhost:8080` | Harbor's dashboard: Maya's password form (missions 2–4), or Sign in with Harbor (mission 8) |
| `http://api.harbor.localhost:8080/api/status/tracking` | the Status API: Basic, API key, opaque Bearer token and JWT checks (missions 1, 5, 6, 9) |
| `http://reports.partner.localhost:8080` | the partner's reporting app: Connect Harbor, OAuth 2.0 with PKCE (mission 7) |
| `http://login.harbor.localhost:8080` | Harbor Sign-in: Keycloak 26.8.2, realm `harbor` |
| `http://coupons.localhost:8080` | another website, with a hidden form aimed at the dashboard (mission 3) |

Every value in the lab is fictional: Maya is `maya` / `demo-only` (Harbor Sign-in's user ID `maya-01`), Harbor Sign-in's
admin console is `admin` / `admin`, and the client secrets are in `keycloak/harbor-realm.json` and `compose.yaml`. Never
type a real password into the lab. Its only port is bound to 127.0.0.1, so nothing outside your computer reaches it.

## The helpers (in the toolbox)

`harbor --help` lists them. `harbor job`, `harbor replay` and `harbor revoke` send a mission's own request and print it
the way it travels, with the answer; `harbor token --fresh` prints each step of its sign-in. The other helpers read the
lab's teaching views or change one of its switches, and say what they did.

| command | mission |
|---|---|
| `harbor requests [N]` | 1: what the Status API received, headers as they arrived |
| `harbor lab samesite none\|lax` | 3: the dashboard's cookie setting, from the next sign-in |
| `harbor replay SESSION_ID`, `harbor lab session-ttl 60` | 4: a session ID from the terminal; one short session (the next sign-in only) |
| `harbor job [--change] [--key K]`, `harbor key show\|rotate\|revoke` | 5 and 9: the reporting job and its key |
| `harbor token [--opaque\|--other-api\|--expired\|--fresh]`, `harbor jwt decode\|edit`, `harbor revoke`, `harbor api-check local\|introspect` | 6: prepared tokens, a fresh one from Harbor Sign-in, decoding, tampering, revocation, introspection |
| `harbor partner tokens\|disconnect\|reuse-code`, `harbor partner wrong-verifier on\|off` | 7: the partner's tokens, Harbor disconnecting it, the extras (a wrong verifier spoils one connection) |
| `harbor lab sign-in harbor\|password`, `harbor session SESSION_ID [--id-token]`, `harbor lab expire-access` | 8: Sign in with Harbor, the session's tokens, a refresh |
| `harbor check` | 9: the job, the dashboard and the partner, right now |
| `harbor lab reset` | any time: every switch back to its starting value, and a working key for the job |

The prepared tokens are signed with Harbor Sign-in's own key: a disposable RSA key that the one-shot `init` service
makes on the first start, imports into Keycloak (so Keycloak signs with it too) and shares with the toolbox.

## When something doesn't work

- **Port 8080 is taken.** See what holds it: `lsof -iTCP:8080 -sTCP:LISTEN` on macOS and Linux,
  `netstat -ano | findstr :8080` on Windows. Or move the lab: put `HARBOR_PORT=8081` (any free port) in a file named
  `.env` next to `compose.yaml`, run `docker compose down -v` and start again. Every address then uses that port.
- **A mission behaves differently from its page.** An extra you tried may still be switched on: `harbor lab reset`.
- **The whole lab, from the start:** `docker compose down -v`, then `docker compose up -d --wait`.
- **Check the lab itself:** `docker compose --profile tests run --rm tests` runs every mission over HTTP (about 15 s)
  and says which check fails. It does the missions itself: it signs Maya in, connects the partner, and rotates and
  revokes the job's key. At the end it puts the switches back and disconnects the partner, but Maya's sessions, the
  job's other keys and the request logs stay, so start from nothing before you do the missions: `docker compose down -v`,
  then `docker compose up -d --wait`.

## Check it in browsers (for the lab's maintainers)

```bash
docker compose --profile tests run --rm -e SLOW=1 tests    # the HTTP checks, plus a revoked token at its exp (5 more minutes)
docker run --rm --network container:harbor-lab-gateway-1 -e HARBOR_PORT="$(docker compose exec -T gateway printenv HARBOR_PORT)" \
  -v "$PWD/tests:/tests:ro" -w /tests \
  mcr.microsoft.com/playwright/python:v1.65.2-noble@sha256:38dd67fc654b56b3cba611e4c8eb71cd33750e1cd29eea2a5dc00b484817a75f \
  sh -c 'pip install -q --break-system-packages playwright==1.65.2 && python3 browsers.py'   # missions 2, 3, 4, 7, 8 in Chromium and Firefox
```

Changed something in `services/`? The lab's image is built only when its tag is new, and the tag is a fingerprint of
`services/`: run `python3 tests/image_tag.py --write`, then `docker compose up -d --wait` builds the new image.

## What's where

- `compose.yaml`: init (builds the lab's image and makes the signing key), keycloak, valkey (the dashboard's shared
  session store), status-api, dashboard-a and dashboard-b, partner, gateway (Caddy: every `*.localhost` name on one
  port), toolbox, tests.
- `services/`: one Python 3.14 image (FastAPI): `status_api.py`, `dashboard.py`, `partner.py`, `harbor.py` (the
  toolbox's helpers), `lab_init.py`, `common.py`.
- `keycloak/harbor-realm.json`: Harbor Sign-in's realm (the signing key is added at the first start).
- `gateway/`: the Caddyfile and the coupons site.
- `tests/`: `missions.py` (HTTP), `browsers.py` (Playwright) and `image_tag.py` (the image's tag).
