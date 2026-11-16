"""Small pieces the exercise's code shares: the addresses, where Harbor Sign-in publishes its keys, and how the lab
shortens secrets on screen."""
import base64
import os

ISSUER = os.environ.get("HARBOR_ISSUER", "http://login.harbor.localhost:8080/realms/harbor")
STATUS_API = os.environ.get("HARBOR_STATUS_API", "http://api.harbor.localhost:8080")
LAB_ADMIN = os.environ.get("HARBOR_LAB_ADMIN", "lab-admin")  # lets the toolbox use the lab-only endpoints

# Where Harbor Sign-in publishes its public keys, under its issuer address (Keycloak's address for them)
CERTS = f"{ISSUER}/protocol/openid-connect/certs"


def short(secret: str | None, keep: int = 6) -> str:
    """How the lab shows a secret on a page: the first characters and an ellipsis, as the video does."""
    return (secret[:keep] + "…") if secret and len(secret) > keep else (secret or "")


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
