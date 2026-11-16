"""Lab only: Harbor Sign-in's disposable signing key, made the first time the lab starts.

Every access token in this lab is signed with one RSA key pair. Harbor Sign-in (Keycloak) signs the tokens it issues
with it, and the toolbox signs the tokens it prepares for the exercises with it, so the Status API checks all of them
against the same published public key. The key is made here, once, and given to Keycloak inside the realm it imports.
It never leaves the lab's Docker volumes; `docker compose down -v` deletes it, and the next start makes a new one.
"""
import base64
import datetime
import hashlib
import json
import os

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

KEYS = "/lab-keys"                            # the private key and the public key set (JWKS)
REALM_IN = "/harbor/realm/harbor-realm.json"  # the realm as written in keycloak/harbor-realm.json
REALM_OUT = "/realm-import/harbor-realm.json"  # what Keycloak imports: the same realm with the key added


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def number(value: int) -> str:
    return b64url(value.to_bytes((value.bit_length() + 7) // 8, "big"))


key_file = f"{KEYS}/signing-key.pem"
if os.path.exists(key_file):
    with open(key_file, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    print("lab-init: kept the existing signing key")
else:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                          serialization.NoEncryption()))
    print("lab-init: made a new signing key")

public_key = private_key.public_key()
public_der = public_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
key_id = b64url(hashlib.sha256(public_der).digest())  # the key ID Keycloak gives an imported RSA key

# The public half, published as a JSON Web Key Set: what an API fetches to check signatures.
numbers = public_key.public_numbers()
jwks = {"keys": [{"kid": key_id, "kty": "RSA", "alg": "RS256", "use": "sig", "n": number(numbers.n), "e": number(numbers.e)}]}
with open(f"{KEYS}/jwks.json", "w") as f:
    json.dump(jwks, f, indent=2)

# Keycloak wants a certificate with an imported key; a self-signed one is enough for a lab.
name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Harbor Sign-in (lab)")])
now = datetime.datetime.now(datetime.timezone.utc)
certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(public_key)
               .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(days=1))
               .not_valid_after(now + datetime.timedelta(days=3650)).sign(private_key, hashes.SHA256()))

with open(REALM_IN) as f:  # the lab's addresses use port 8080, or HARBOR_PORT when it is set
    realm = json.loads(f.read().replace("localhost:8080", "localhost:" + os.environ.get("HARBOR_PORT", "8080")))
pkcs8 = private_key.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
realm.setdefault("components", {})["org.keycloak.keys.KeyProvider"] = [{
    "name": "harbor-lab-signing-key",
    "providerId": "rsa",
    "subComponents": {},
    "config": {
        "priority": ["200"],
        "enabled": ["true"],
        "active": ["true"],
        "algorithm": ["RS256"],
        "keyUse": ["SIG"],
        "privateKey": [base64.b64encode(pkcs8).decode()],
        "certificate": [base64.b64encode(certificate.public_bytes(serialization.Encoding.DER)).decode()],
    },
}]
with open(REALM_OUT, "w") as f:
    json.dump(realm, f, indent=2)
os.chmod(REALM_OUT, 0o644)
os.chmod(key_file, 0o644)  # a lab key, read by the toolbox; never do this with a real one
print(f"lab-init: Harbor Sign-in signs with key {key_id}")
