"""The browser missions (2, 3, 4, 7 and 8) in real browsers: Chromium and Firefox, Playwright's builds.

Runs in a container that shares the gateway's network, so every *.localhost name the browsers send to 127.0.0.1 reaches
the gateway on the lab's port (8080, or HARBOR_PORT), as on the learner's computer. With the lab up, from its folder:

    docker run --rm --network container:harbor-lab-gateway-1 -e HARBOR_PORT -v "$PWD/tests:/tests:ro" -w /tests \
      mcr.microsoft.com/playwright/python:v1.65.2-noble@sha256:38dd67fc654b56b3cba611e4c8eb71cd33750e1cd29eea2a5dc00b484817a75f \
      sh -c 'pip install -q --break-system-packages playwright==1.65.2 && python3 browsers.py'

Prints PASS or FAIL for every check (INFO for WebKit, which isn't a supported browser for these missions) and exits 1
if any check failed. WebKit here is the Linux build, not Safari. Lab values only.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright

PORT = os.environ.get("HARBOR_PORT") or "8080"
DASH = f"http://dashboard.harbor.localhost:{PORT}"
PARTNER = f"http://reports.partner.localhost:{PORT}"
COUPONS = f"http://coupons.localhost:{PORT}"
SIGN_IN_HOST = "login.harbor.localhost"
HEALTHY = "Tracking service — Healthy"
ADMIN = {"X-Lab-Admin": "lab-admin"}
FAILED: list[str] = []
COUNT = 0


def check(engine: str, name: str, ok, detail=""):
    global COUNT
    COUNT += 1
    print(f"{'PASS' if ok else 'FAIL'}  [{engine}] {name}", flush=True)
    if not ok:
        FAILED.append(f"[{engine}] {name}")
        print("      " + str(detail)[:1200].replace("\n", "\n      "), flush=True)


def call(host: str, method: str, path: str, json_body=None, form=None, headers=None) -> tuple[int, str]:
    """A direct request through the gateway (the terminal's view), by name, without DNS."""
    data, sent = None, {"Host": f"{host}:{PORT}", **(headers or {})}
    if json_body is not None:
        data, sent["Content-Type"] = json.dumps(json_body).encode(), "application/json"
    elif form is not None:
        data, sent["Content-Type"] = urllib.parse.urlencode(form).encode(), "application/x-www-form-urlencoded"
    request = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=data, method=method, headers=sent)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def lab_config(**changes):
    return call("dashboard.harbor.localhost", "POST", "/lab/config", json_body=changes, headers=ADMIN)


def lab_reset():
    """`harbor lab reset`, for the dashboard's switches: the password form, SameSite=Lax, 30-minute sessions."""
    return call("dashboard.harbor.localhost", "POST", "/lab/reset", headers=ADMIN)


def replay(session_id: str) -> int:
    return call("dashboard.harbor.localhost", "GET", "/status", headers={"Cookie": f"session={session_id}"})[0]


def newest_request(path: str) -> dict:
    entries = json.loads(call("dashboard.harbor.localhost", "GET", "/lab/requests")[1])
    return next((e for e in entries if e["path"] == path), {})


def remove_partner_grant():
    """`harbor partner disconnect`: Harbor Sign-in's admin API removes Maya's grant, so the consent screen shows again."""
    _, answer = call(SIGN_IN_HOST, "POST", "/realms/master/protocol/openid-connect/token",
                     form={"grant_type": "password", "client_id": "admin-cli", "username": "admin", "password": "admin"})
    token = json.loads(answer)["access_token"]
    call(SIGN_IN_HOST, "DELETE", "/admin/realms/harbor/users/maya-01/consents/partner-reports",
         headers={"Authorization": f"Bearer {token}"})


def session_cookie(context) -> dict:
    return next((c for c in context.cookies(DASH) if c["name"] == "session"), {})


def password_sign_in(page) -> dict:
    page.goto(f"{DASH}/login")
    page.fill("#username", "maya")
    page.fill("#password", "demo-only")
    page.click("#sign-in")
    page.wait_for_load_state()
    return session_cookie(page.context)


def harbor_sign_in_form(page) -> str:
    """Harbor Sign-in's own page: type Maya's password there, and only there. Returns the host it was typed on."""
    page.wait_for_selector("#password", timeout=20000)
    host = urllib.parse.urlparse(page.url).hostname
    page.fill("#username", "maya")
    page.fill("#password", "demo-only")
    page.click("#kc-login")
    page.wait_for_load_state()
    return host


def alerts_to(page) -> str:
    page.goto(f"{DASH}/")
    return page.input_value("input[name=alerts_to]")


def log_out(page):
    page.goto(f"{DASH}/")
    page.click("#logout")
    page.wait_for_load_state()


def missions(engine: str, browser):
    lab_reset()

    # Mission 2: a browser login
    context = browser.new_context()
    page = context.new_page()
    seen_responses = []
    page.on("response", lambda response: seen_responses.append(response))
    page.goto(f"{DASH}/")
    check(engine, "2 signed out, the dashboard opens its sign-in page", page.url == f"{DASH}/login", page.url)
    cookie = password_sign_in(page)
    posted = next((r for r in seen_responses if r.request.method == "POST" and r.url == f"{DASH}/login"), None)
    set_cookie = posted.header_value("set-cookie") if posted else None  # response.headers leaves cookie headers out
    check(engine, "2 the sign-in's answer: Set-Cookie: session=...; Secure; HttpOnly; SameSite=Lax; Path=/",
          posted and re.fullmatch(r"session=[\w-]{43}; Secure; HttpOnly; SameSite=Lax; Path=/", set_cookie or ""),
          (posted and posted.status, set_cookie))
    check(engine, "2 the browser keeps the cookie: Secure, HttpOnly, SameSite=Lax, Path=/",
          cookie.get("secure") and cookie.get("httpOnly") and cookie.get("sameSite") == "Lax" and cookie.get("path") == "/", cookie)
    check(engine, "2 the status card: Tracking service — Healthy", page.inner_text("#status") == HEALTHY, page.url)
    page.click("#refresh")
    page.wait_for_load_state()
    entry = newest_request("/")
    check(engine, "2 Refresh sends Cookie: session=... (and no password)", entry.get("cookie", "").startswith("session=")
          and entry.get("status") == 200, entry)
    check(engine, "2 the console's document.cookie can't see the session cookie (HttpOnly)",
          "session=" not in page.evaluate("document.cookie"), page.evaluate("document.cookie"))
    page.goto(f"{DASH}/lab/session")
    record = json.loads(page.inner_text("body"))
    check(engine, "2 the server's session record: Maya and an expiry time",
          record.get("user") == "maya" and record.get("expires_in_seconds", 0) > 1700, record)
    servers = set()
    for _ in range(4):
        page.goto(f"{DASH}/")
        match = re.search(r"Served by (dashboard-[ab])", page.inner_text("body"))
        servers.add(match.group(1) if match else None)
    check(engine, "2 extra: both dashboard servers serve Maya with the same cookie", servers == {"dashboard-a", "dashboard-b"}, servers)

    # Mission 3: a request from another site
    before = alerts_to(page)
    page.goto(f"{COUPONS}/")
    page.wait_for_url(f"{DASH}/alerts", timeout=20000)
    check(engine, "3 the coupons page's hidden form arrives without Maya's cookie: 401, nothing changed",
          "Not signed in" in page.inner_text("body"), page.inner_text("body")[:300])
    entry = newest_request("/alerts")
    check(engine, "3 the dashboard's record: no cookie, Sec-Fetch-Site: cross-site, 401",
          entry.get("cookie") == "(none)" and entry.get("sec-fetch-site") == "cross-site" and entry.get("status") == 401, entry)
    check(engine, "3 where Maya's alerts go didn't change", alerts_to(page) == before)
    lab_config(samesite="None")
    page.click("#logout")
    page.wait_for_load_state()
    cookie = password_sign_in(page)
    check(engine, "3 extra: after harbor lab samesite none and a new sign-in, the cookie says SameSite=None",
          cookie.get("sameSite") == "None", cookie)
    page.goto(f"{COUPONS}/")
    page.wait_for_url(f"{DASH}/alerts", timeout=20000)
    entry = newest_request("/alerts")
    check(engine, "3 extra: now the cookie travels, and Harbor's CSRF check stops the change: 403",
          "Refused" in page.inner_text("body") and entry.get("cookie", "").startswith("session=") and entry.get("status") == 403
          and (entry.get("note") or "").startswith(f"CSRF check failed: it didn't come from Harbor's own page (Origin: {COUPONS})"),
          entry)
    check(engine, "3 extra: where Maya's alerts go didn't change", alerts_to(page) == before)
    lab_config(samesite="Lax")

    # Mission 4: log out and replay
    page.click("#logout")
    page.wait_for_load_state()
    first = password_sign_in(page).get("value", "")
    check(engine, "4 the copied session ID works from the terminal while signed in", replay(first) == 200)
    page.click("#logout")
    page.wait_for_load_state()
    check(engine, "4 log out: back on the sign-in page, the cookie gone from the browser",
          page.url == f"{DASH}/login" and not session_cookie(context), (page.url, session_cookie(context)))
    check(engine, "4 the old ID replayed from the terminal: 401", replay(first) == 401)
    second = password_sign_in(page).get("value", "")
    check(engine, "4 signing in again: a new ID that works, and the old one stays dead",
          second and second != first and replay(second) == 200 and replay(first) == 401)

    # Mission 7: the partner connects (the same browser, as a learner goes on)
    remove_partner_grant()
    page.goto(f"{PARTNER}/")
    page.click("#connect")
    page.wait_for_load_state()
    shown = dict(re.findall(r"^(\S+)\t(.*)$", page.inner_text("table"), re.M))
    check(engine, "7 Connect Harbor shows the request before the browser leaves",
          shown.get("client_id") == "partner-reports" and shown.get("scope") == "status:read" and shown.get("code_challenge_method") == "S256"
          and shown.get("state") and shown.get("code_challenge") and shown.get("redirect_uri") == f"{PARTNER}/callback", shown)
    page.click("#continue")
    typed_on = harbor_sign_in_form(page)
    check(engine, "7 the password is typed on Harbor Sign-in's own page", typed_on == SIGN_IN_HOST, typed_on)
    consent = page.inner_text("body")
    check(engine, "7 the consent screen: Partner Reports asks to Read tracking status",
          "Read tracking status" in consent and page.locator("[name=accept]").count() == 1, consent[:300])
    with page.expect_navigation(url=re.compile(re.escape(f"{PARTNER}/callback")), timeout=20000):
        page.click("[name=accept]")  # Keycloak 26.8: <button name="accept">
    address = urllib.parse.parse_qs(urllib.parse.urlparse(page.url).query)
    check(engine, "7 the address bar: a code and the state, and no token",
          address.get("code") and address.get("state") and not any("token" in k for k in address), page.url[:200])
    check(engine, "7 the backend's token exchange is shown, and the report says Healthy",
          '"code_verifier"' in page.inner_text("#exchange") and page.inner_text("#report") == HEALTHY, page.inner_text("body")[:400])
    stored = page.evaluate("[localStorage.length, sessionStorage.length, document.cookie]")
    check(engine, "7 the partner's page holds no token: no storage, no readable cookie", stored == [0, 0, ""], stored)
    page.reload()
    check(engine, "7 reloading the callback: the code works once", "used once" in page.inner_text("body"), page.inner_text("body")[:300])

    # Mission 8 in order, in the same browser: still signed in with the password from mission 4 until Log out; then
    # Sign in with Harbor comes straight back, because Maya signed in on Harbor Sign-in in mission 7 (single sign-on).
    lab_config(signin="harbor")
    page.goto(f"{DASH}/")
    still = "with a password" in page.inner_text("body")
    log_out(page)
    page.click("#sign-in-with-harbor")
    page.wait_for_url(f"{DASH}/", timeout=20000)
    check(engine, "8 in order: the password session lasts until Log out; then Sign in with Harbor needs no password (SSO)",
          still and "with Harbor Sign-in" in page.inner_text("body") and page.inner_text("#status") == HEALTHY,
          (still, page.inner_text("body")[:300]))
    context.close()

    # Mission 8 in a fresh browser: the password on Harbor Sign-in, and the tokens
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{DASH}/login")
    page.click("#sign-in-with-harbor")
    typed_on = harbor_sign_in_form(page)
    page.wait_for_url(f"{DASH}/", timeout=20000)
    check(engine, "8 Sign in with Harbor: the password on Harbor Sign-in, back on the dashboard, Healthy",
          typed_on == SIGN_IN_HOST and "with Harbor Sign-in" in page.inner_text("body") and page.inner_text("#status") == HEALTHY,
          page.inner_text("body")[:300])
    names = sorted(c["name"] for c in context.cookies(DASH))
    stored = page.evaluate("[localStorage.length, sessionStorage.length, document.cookie]")
    check(engine, "8 the browser holds only the session cookie: no tokens in storage, none a script can read",
          names == ["session"] and stored == [0, 0, ""], (names, stored))
    page.goto(f"{DASH}/lab/session")
    kept = json.loads(page.inner_text("body")).get("tokens_kept_with_the_session", {})
    check(engine, "8 the session record keeps the ID, access and refresh tokens on the server",
          kept.get("id_token", {}).get("claims", {}).get("aud") == "harbor-dashboard"
          and kept.get("access_token", {}).get("claims", {}).get("aud") == "harbor-status-api"
          and kept.get("refresh_token", {}).get("goes_only_to") == "Harbor Sign-in", kept)
    page.goto(f"{DASH}/")
    call("dashboard.harbor.localhost", "POST", "/lab/expire-access", headers=ADMIN)  # harbor lab expire-access, then Refresh
    page.click("#refresh")
    page.wait_for_load_state()
    page.goto(f"{DASH}/lab/trace")
    steps = " | ".join(f"{s['step']}: {s['detail']}" for s in json.loads(page.inner_text("body"))["steps"])
    check(engine, "8 Refresh, then the trace: the cookie, the session, a refresh, Bearer, the API's checks, Healthy",
          all(w in steps for w in ("Cookie: session=", "found the session", "grant_type=refresh_token", "Authorization: Bearer",
                                    "signature", "issuer, audience, expiry", "permission status:read: yes", HEALTHY)), steps)
    context.close()
    lab_reset()


def webkit_note(browser):
    """WebKit (the engine behind Safari) with the password form: does it keep a Secure cookie on http://*.localhost?"""
    lab_reset()
    context = browser.new_context()
    page = context.new_page()
    cookie = password_sign_in(page)
    print(f"INFO  [webkit] the session cookie {'was kept' if cookie else 'was refused'} on http://dashboard.harbor.localhost "
          f"(Secure on plain HTTP); the page shows: {page.url}", flush=True)
    context.close()


with sync_playwright() as p:
    for name in sys.argv[1:] or ["chromium", "firefox", "webkit"]:
        engine = getattr(p, name).launch()
        try:
            webkit_note(engine) if name == "webkit" else missions(name, engine)
        except Exception as error:  # a step that couldn't run is a failure, with what went wrong
            check(name, "the browser missions ran to the end", False, f"{type(error).__name__}: {error}")
        finally:
            engine.close()
    lab_reset()
    remove_partner_grant()  # the partner as on a first visit: no grant, no connection (mission 7's consent screen)
    call("reports.partner.localhost", "POST", "/lab/forget", headers=ADMIN)

print(f"\n{COUNT - len(FAILED)} of {COUNT} browser checks passed" + (f"; failed: {'; '.join(FAILED)}" if FAILED else ""), flush=True)
sys.exit(1 if FAILED else 0)
