"""One HTTP request from inside the lab's network, printed whole. The slim image has no curl.

    python -m tools.http GET  http://receiving-agent:8000/health
    python -m tools.http POST http://receiving-agent:8000/ask '{"question": "What arrived for purchase order PO-2207?"}'
"""
import json
import sys
import urllib.error
import urllib.request

method, url = sys.argv[1], sys.argv[2]
data = sys.argv[3].encode() if len(sys.argv) > 3 else None
headers = {"Content-Type": "application/json"}
for extra in sys.argv[4:]:      # extra headers, each as "Name: value"
    name, _, value = extra.partition(":")
    headers[name.strip()] = value.strip()
request = urllib.request.Request(url, data=data, method=method, headers=headers)
try:
    response = urllib.request.urlopen(request, timeout=120)
except urllib.error.HTTPError as error:
    response = error
print(f"{method} {url}")
if data:
    print(data.decode())
print(f"\nHTTP {response.status}, {response.headers.get('Content-Type')}")
body = response.read().decode()
try:
    print(json.dumps(json.loads(body), indent=2))
except ValueError:
    print(body)
