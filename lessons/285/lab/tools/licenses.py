"""List every installed Python package with its version and its declared license, and check what must be absent.

    python -m tools.licenses
"""
from importlib.metadata import distributions

NOT_OPEN_SOURCE = {"langgraph-api", "langgraph-cli", "langgraph-runtime-inmem", "arize-phoenix"}
rows = []
for dist in distributions():
    meta = dist.metadata
    declared = meta.get("License-Expression") or ""
    if not declared:
        classifiers = [c.split("::")[-1].strip() for c in meta.get_all("Classifier") or [] if c.startswith("License ::")]
        declared = "; ".join(classifiers) or " ".join((meta.get("License") or "not declared").split())[:60]
    rows.append((meta["Name"], dist.version, declared))
for name, version, declared in sorted(rows, key=lambda r: r[0].lower()):
    print(f"{name:<34} {version:<12} {declared}")
found = sorted(name for name, _, _ in rows if name.lower() in NOT_OPEN_SOURCE)
print(f"\n{len(rows)} packages installed")
print("installed packages that are not open source (langgraph-api, langgraph-cli, langgraph-runtime-inmem, arize-phoenix):",
      ", ".join(found) or "none")
