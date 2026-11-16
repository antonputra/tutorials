"""Small pieces Harbor's services share: addresses, Harbor Sign-in's endpoints, a plain page, and how the lab shortens
secrets on screen."""
import base64
import hashlib
import html
import os
import secrets

ISSUER = os.environ.get("HARBOR_ISSUER", "http://login.harbor.localhost:8080/realms/harbor")
STATUS_API = os.environ.get("HARBOR_STATUS_API", "http://api.harbor.localhost:8080")
DASHBOARD = os.environ.get("HARBOR_DASHBOARD", "http://dashboard.harbor.localhost:8080")
PARTNER = os.environ.get("HARBOR_PARTNER", "http://reports.partner.localhost:8080")
LAB_ADMIN = os.environ.get("HARBOR_LAB_ADMIN", "lab-admin")  # lets the toolbox use the lab-only endpoints

# Harbor Sign-in's endpoints (Keycloak's addresses under the issuer)
AUTHORIZE = f"{ISSUER}/protocol/openid-connect/auth"
TOKEN = f"{ISSUER}/protocol/openid-connect/token"
CERTS = f"{ISSUER}/protocol/openid-connect/certs"
REVOKE = f"{ISSUER}/protocol/openid-connect/revoke"
INTROSPECT = f"{ISSUER}/protocol/openid-connect/token/introspect"

STYLE = """
body { font: 16px/1.5 system-ui, sans-serif; background: #070b13; color: #e6e9ef; max-width: 52rem; margin: 2rem auto; padding: 0 1rem; }
a, button { color: #58a6ff; } h1 { font-size: 1.5rem; } h2 { font-size: 1.15rem; } code, pre { background: #131924; padding: .1rem .3rem; border-radius: 4px; }
pre { padding: .75rem; overflow-x: auto; white-space: pre-wrap; word-break: break-all; }
.card { background: #1b2433; border: 1px solid #353d4d; border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0; }
.ok { color: #56d364; } .no { color: #e46c71; } .lab { border-style: dashed; } .muted { color: #afb8c8; }
button, .button { background: #1b2433; border: 1px solid #58a6ff; border-radius: 6px; padding: .4rem .9rem; cursor: pointer; text-decoration: none; font: inherit; }
input { font: inherit; padding: .3rem .5rem; background: #131924; color: #e6e9ef; border: 1px solid #353d4d; border-radius: 4px; }
form.inline { display: inline; } label { display: block; margin: .5rem 0; } table { border-collapse: collapse; } td, th { padding: .2rem .6rem; text-align: left; vertical-align: top; }
"""


def page(title: str, body: str) -> str:
    return f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width'>" \
           f"<link rel=icon href='data:,'>" \
           f"<title>{html.escape(title)}</title><style>{STYLE}</style></head><body>{body}</body></html>"


def short(secret: str | None, keep: int = 6) -> str:
    """How the lab shows a secret on a page: the first characters and an ellipsis, as the video does."""
    return (secret[:keep] + "…") if secret and len(secret) > keep else (secret or "")


def lab_note(text: str) -> str:
    return f"<div class='card lab'><p class='muted'>Lab only: {text}</p></div>"


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def new_pkce() -> tuple[str, str]:
    """PKCE: a random verifier the backend keeps, and its SHA-256 hash, the challenge, which goes in the request."""
    verifier = b64url(secrets.token_bytes(32))
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge
