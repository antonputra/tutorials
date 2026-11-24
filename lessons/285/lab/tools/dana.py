"""Stands in for Dana at the approval gate: asks the payables service where a run stands and approves each
payment it waits for, over HTTP, until the run is finished. Prints one line a decision.

    python -m tools.dana <thread_id> [--quiet]

It knows nothing about the agent. It is only a caller of the service, like a web page would be. If the service
does not answer (it was killed, say), it says so and keeps asking; if the run is stopped, it tells the service
to carry on.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("PAYABLES_AGENT_URL", "http://payables-agent:8000")
HEADERS = {"Content-Type": "application/json", "X-Service-Token": os.environ.get("SERVICE_TOKEN", "")}


def call(method: str, path: str, body=None):
    request = urllib.request.Request(BASE + path, method=method, headers=HEADERS,
                                     data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)
    except (urllib.error.URLError, ConnectionError, TimeoutError) as error:
        return 0, {"detail": str(getattr(error, "reason", error))}


def main(thread_id: str, quiet: bool) -> None:
    started, approved, down, last = time.monotonic(), 0, False, None
    stamp = lambda: f"{time.monotonic() - started:7.2f} s"
    while True:
        code, now = call("GET", f"/runs/{thread_id}")
        if code == 0:
            if not down:
                print(f"{stamp()}  the service does not answer ({now['detail']}); asking again every half second", flush=True)
            down = True
            time.sleep(0.5)
            continue
        if down:
            print(f"{stamp()}  the service answers again", flush=True)
            down = False
        status = now.get("status", f"HTTP {code}: {now.get('detail')}")
        if status == "waiting_for_a_person":
            asked = now["waiting_for"]
            code, sent = call("POST", f"/runs/{thread_id}/decision", {"type": "approve"})
            if code == 202:
                approved += 1
                if not quiet or approved <= 3:
                    print(f"{stamp()}  approve {approved}: {asked['tool']} invoice {asked['args'].get('invoice_number')}, "
                          f"${asked['args'].get('amount_usd'):,.2f}, note: {asked['args'].get('note')}", flush=True)
                elif approved == 4:
                    print("          ... (--quiet: the next approvals are not printed)", flush=True)
        elif status == "stopped":
            code, sent = call("POST", "/runs", {"thread_id": thread_id})
            print(f"{stamp()}  the run is stopped with {now['messages_saved']} messages saved, next {now.get('next')}; "
                  f"told the service to carry on: {sent.get('started')}", flush=True)
        elif status == "finished":
            print(f"{stamp()}  finished: {approved} payments approved, {now['messages_saved']} messages saved\n")
            print(now["result"])
            return
        elif status != "working":
            if status != last:
                print(f"{stamp()}  {status}", flush=True)
            if code in (401, 404):
                sys.exit(1)
        last = status
        time.sleep(0.05)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], "--quiet" in sys.argv)
