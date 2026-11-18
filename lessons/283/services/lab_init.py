"""Lab only: Harbor Sign-in's disposable signing key, made the first time the exercise starts.

The exercise has no sign-in service running, only what an API needs from one: its published public keys. This makes an
RSA key pair, keeps the private half for the toolbox, which signs the tokens prepared for the exercise with it, and
publishes the public half as a JSON Web Key Set at Harbor Sign-in's address, where the Status API fetches it to check
signatures. `docker compose down -v` deletes the key; the next start makes a new one.
"""
import base64
import hashlib
import json
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

KEYS = "/lab-keys"        # the private key and the key set, for the toolbox
PUBLISHED = "/published"  # the key set alone, which the gateway publishes


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
key_id = b64url(hashlib.sha256(public_der).digest())  # the key ID Keycloak gives an imported RSA key, as in the full lab

# The public half, published as a JSON Web Key Set: what an API fetches to check signatures.
numbers = public_key.public_numbers()
jwks = {"keys": [{"kid": key_id, "kty": "RSA", "alg": "RS256", "use": "sig", "n": number(numbers.n), "e": number(numbers.e)}]}
for folder in (KEYS, PUBLISHED):
    with open(f"{folder}/jwks.json", "w") as f:
        json.dump(jwks, f, indent=2)
    os.chmod(f"{folder}/jwks.json", 0o644)
os.chmod(key_file, 0o644)  # a lab key, read by the toolbox; never do this with a real one
print(f"lab-init: Harbor Sign-in signs with key {key_id}")
