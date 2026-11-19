"""The small status app from "Docker Explained: How Containers Actually Work".

GET /status reads /app/message.txt, adds one line to /data/requests.log and
sends the message back as a page. It uses only Python's standard library.
"""

import argparse
import html
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

MESSAGE_FILE = Path("/app/message.txt")
LOG_FILE = Path("/data/requests.log")

leak_mb = 0  # --leak-mb N switches on a deliberate bug: keep N MB after every visit
kept = []


class StatusPage(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_error(404)
            return

        message = MESSAGE_FILE.read_text(encoding="utf-8").strip()

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write(f"{now} {self.client_address[0]} GET /status\n")

        if leak_mb:
            kept.append(b"x" * (leak_mb * 1024 * 1024))

        page = "<!doctype html><title>Status</title><h1>" + html.escape(message) + "</h1>\n"
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--leak-mb", type=int, default=0)
    args = parser.parse_args()
    leak_mb = args.leak_mb
    HTTPServer((args.listen, args.port), StatusPage).serve_forever()
