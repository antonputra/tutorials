"""The services' image tag in compose.yaml: a fingerprint of ./services, for the maintainers and the CI.

The image is built from ./services only when its tag is missing (the first start), never pulled from a registry, and
never rebuilt on a later start: a rebuild can change the image's ID (Docker's containerd image store keeps a provenance
attestation with every build), and Compose recreates every container whose image ID changed. So the tag changes with
the code instead: a copy with changed services builds an image of its own.

    python3 tests/image_tag.py           print the fingerprint of ./services
    python3 tests/image_tag.py --check   exit 1 unless compose.yaml's tag is that fingerprint (the CI runs this)
    python3 tests/image_tag.py --write   put it into compose.yaml, after a change in ./services
"""
import hashlib
import pathlib
import re
import sys

FOLDER = pathlib.Path(__file__).resolve().parent.parent
COMPOSE = FOLDER / "compose.yaml"
IMAGE = re.compile(r"^(\s*image: harbor-[a-z]+/services:)(\S+)", re.M)


def fingerprint():
    """SHA-256 over every file in ./services (names and contents, LF line endings), the first 12 hex digits."""
    services = FOLDER / "services"
    files = {}
    for path in services.rglob("*"):
        parts = path.relative_to(services).parts
        if path.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in parts):
            files["/".join(parts)] = path
    digest = hashlib.sha256()
    for name in sorted(files):
        digest.update(name.encode() + b"\0" + files[name].read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return digest.hexdigest()[:12]


def main():
    want = fingerprint()
    with open(COMPOSE, encoding="utf-8", newline="") as f:
        text = f.read()
    found = IMAGE.findall(text)
    if len(found) != 1:
        sys.exit(f"compose.yaml: expected one 'image: harbor-.../services:...' line, found {len(found)}")
    have = found[0][1]
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "--write":
        with open(COMPOSE, "w", encoding="utf-8", newline="") as f:
            f.write(IMAGE.sub(lambda m: m.group(1) + want, text))
        print(f"compose.yaml: {have} -> {want}" if have != want else f"compose.yaml: {want}, unchanged")
    elif action == "--check":
        if have != want:
            sys.exit(f"compose.yaml's image tag is {have}, but ./services is {want}: run python3 tests/image_tag.py --write")
        print(f"compose.yaml's image tag matches ./services: {want}")
    elif action:
        sys.exit(__doc__)
    else:
        print(want)


main()
