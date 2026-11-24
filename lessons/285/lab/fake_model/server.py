"""The scripted model's HTTP side: an OpenAI-compatible Chat Completions endpoint, standard library only.

    POST /v1/chat/completions    the one call a model serves (tool calls included; "stream": true also works)
    POST /control                {"tag": "step-4", "delay_ms": 800, "fresh": true}: the log folder (emptied first when
                                 fresh) and the wait before each reply
    GET  /health

Every request is written to its own file before the reply is computed: LOG_DIR/<tag>/NNNN.request.json.
That file is the evidence: it holds exactly what the agent sent, the messages, the tools and the model name.
The reply goes to NNNN.reply.json. The Authorization header is never written.
"""
import json
import os
import re
import shutil
import threading
import time
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from fake_model import script

LOG_DIR = Path(os.environ.get("LOG_DIR", "/logs"))
STATE = {"tag": "default", "delay_ms": 0}
LOCK = threading.Lock()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def next_seq(tag: str) -> int:
    """Numbers go on from the last file in the folder, so a run that is resumed keeps one sequence."""
    folder = LOG_DIR / tag
    folder.mkdir(parents=True, exist_ok=True)
    seen = [int(p.name[:4]) for p in folder.glob("[0-9][0-9][0-9][0-9].request.json")]
    return max(seen, default=0) + 1


def write(tag: str, seq: int, kind: str, data: dict) -> None:
    path = LOG_DIR / tag / f"{seq:04d}.{kind}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False))
    tmp.rename(path)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):   # the request files are the log
        pass

    def send_json(self, status: int, data: dict) -> None:
        raw = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            return self.send_json(200, {"ok": True, **STATE})
        if self.path == "/v1/models":
            return self.send_json(200, {"object": "list", "data": [{"id": "scripted-1", "object": "model"}]})
        self.send_json(404, {"error": {"message": f"the scripted model has no {self.path}"}})

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if self.path == "/control":
            wanted = json.loads(raw or b"{}")
            with LOCK:
                if "tag" in wanted:
                    STATE["tag"] = re.sub(r"[^a-z0-9-]", "-", str(wanted["tag"]).lower()) or "default"
                    if wanted.get("fresh"):
                        shutil.rmtree(LOG_DIR / STATE["tag"], ignore_errors=True)
                if "delay_ms" in wanted:
                    STATE["delay_ms"] = int(wanted["delay_ms"])
                return self.send_json(200, dict(STATE))
        with LOCK:
            tag, delay_ms = STATE["tag"], STATE["delay_ms"]
            seq = next_seq(tag)
            headers = {k.lower(): v for k, v in self.headers.items() if k.lower() != "authorization"}
            try:
                body = json.loads(raw)
            except ValueError:
                body = None
            write(tag, seq, "request", {"seq": seq, "tag": tag, "received_at": now(), "path": self.path,
                                        "headers": headers, "body_bytes": len(raw), "body": body})
        if self.path != "/v1/chat/completions" or body is None:
            error = {"error": {"message": f"the scripted model only serves POST /v1/chat/completions, not {self.path}",
                               "type": "invalid_request_error"}}
            write(tag, seq, "reply", {"seq": seq, "sent_at": now(), "status": 404, "reply": error})
            return self.send_json(404, error)
        try:
            answer = script.reply(body)
        except Exception:
            error = {"error": {"message": "the script failed: " + traceback.format_exc(), "type": "server_error"}}
            write(tag, seq, "reply", {"seq": seq, "sent_at": now(), "status": 500, "reply": error})
            return self.send_json(500, error)
        answer.update({"id": f"chatcmpl-scripted-{tag}-{seq:04d}", "created": int(time.time()),
                       "system_fingerprint": "scripted-stand-in"})
        time.sleep(delay_ms / 1000)
        write(tag, seq, "reply", {"seq": seq, "sent_at": now(), "status": 200, "delay_ms": delay_ms, "reply": answer})
        if not body.get("stream"):
            return self.send_json(200, answer)
        # Streaming, for a client that insists: the whole message in one chunk, then the end.
        message = answer["choices"][0]["message"]
        delta = {"role": "assistant", "content": message.get("content")}
        if message.get("tool_calls"):
            delta["tool_calls"] = [dict(tc, index=i) for i, tc in enumerate(message["tool_calls"])]
        base = {"id": answer["id"], "object": "chat.completion.chunk", "created": answer["created"], "model": answer["model"]}
        chunks = [dict(base, choices=[{"index": 0, "delta": delta, "finish_reason": None}]),
                  dict(base, choices=[{"index": 0, "delta": {}, "finish_reason": answer["choices"][0]["finish_reason"]}]),
                  dict(base, choices=[], usage=answer["usage"])]
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        self.end_headers()
        for chunk in chunks:
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
        self.wfile.write(b"data: [DONE]\n\n")
        self.close_connection = True


if __name__ == "__main__":
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"scripted model on :8080, logging requests under {LOG_DIR}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
