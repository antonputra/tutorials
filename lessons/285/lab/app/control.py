"""Only for the scripted stand-in: choose the folder its request log goes to, and its wait before each reply.

    python -m app.control <tag> [delay in ms] [keep]     keep: do not empty the tag's folder first

With a real model FAKE_MODEL_CONTROL is empty and this does nothing.
"""
import json
import os
import sys
import urllib.request


def begin(tag: str, delay_ms: int | None = 0, fresh: bool = True) -> None:
    """delay_ms None leaves the wait as it is set."""
    url = os.environ.get("FAKE_MODEL_CONTROL")
    if not url:
        return
    wanted = {"tag": tag, "fresh": fresh, **({} if delay_ms is None else {"delay_ms": delay_ms})}
    request = urllib.request.Request(url, data=json.dumps(wanted).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request) as response:
        state = json.load(response)
    print(f"[scripted model: request log /logs/{state['tag']}, {state['delay_ms']} ms before each reply]", flush=True)


if __name__ == "__main__":
    begin(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0, fresh="keep" not in sys.argv[3:])
