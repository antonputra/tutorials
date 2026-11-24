"""Read the scripted model's request log: what the agent really sent to the model, call by call.

    python -m tools.reqlog tags                     the log folders and how many requests each holds
    python -m tools.reqlog ls <tag>                 one line a request: time, size, messages, tools, and the reply
    python -m tools.reqlog sizes <tag>              the size of each request, and the total
    python -m tools.reqlog tools <tag> <seq>        the tools on offer in that request (--full: with descriptions)
    python -m tools.reqlog system <tag> <seq>       the system prompt of that request
    python -m tools.reqlog messages <tag> <seq>     every message of that request, long text cut (--max N)
    python -m tools.reqlog raw <tag> <seq>          the request body as JSON, long text cut (--max N)
    python -m tools.reqlog find <tag> <text>        which requests hold the text, and in which message
    python -m tools.reqlog same <tag> <a> <b>       are two requests the same, byte for byte?
    python -m tools.reqlog split <tag>              the requests grouped by who sent them (by system prompt)
    python -m tools.reqlog searches <tag>           what search_policy answered in that run: each question, and the
                                                    rows it got back with their distances
"""
import hashlib
import json
import sys
from pathlib import Path

LOG = Path("/logs")


def text_of(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return "".join(p.get("text", "") for p in content if isinstance(p, dict))


def load(tag: str, seq: int, kind: str = "request"):
    path = LOG / tag / f"{seq:04d}.{kind}.json"
    return json.loads(path.read_text()) if path.exists() else None


def seqs(tag: str):
    return sorted(int(p.name[:4]) for p in (LOG / tag).glob("*.request.json"))


def one_line(text: str, width: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 3] + "..."


def reply_summary(tag: str, seq: int, width: int = 90) -> str:
    out = load(tag, seq, "reply")
    if out is None:
        return "(no reply was sent)"
    if out.get("status") != 200:
        return f"HTTP {out.get('status')}: " + one_line(json.dumps(out["reply"]), width)
    message = out["reply"]["choices"][0]["message"]
    if message.get("tool_calls"):
        return " + ".join(f"{tc['function']['name']}({one_line(tc['function']['arguments'], width)})"
                          for tc in message["tool_calls"])
    return "text: " + one_line(message.get("content") or "", width)


def cut(value, limit: int):
    if isinstance(value, str) and len(value) > limit:
        return value[:limit] + f"... [{len(value):,} characters in all]"
    if isinstance(value, list):
        return [cut(v, limit) for v in value]
    if isinstance(value, dict):
        return {k: cut(v, limit) for k, v in value.items()}
    return value


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, args = argv[0], argv[1:]
    limit = int(args[args.index("--max") + 1]) if "--max" in args else 300
    if cmd == "tags":
        for folder in sorted(p for p in LOG.iterdir() if p.is_dir()):
            print(f"{folder.name:<28} {len(list(folder.glob('*.request.json'))):>4} requests")
        return
    tag = args[0]
    if cmd == "ls":
        print(f"{'seq':>4}  {'received (UTC)':<12}  {'bytes':>8}  {'msgs':>4}  {'tools':>5}  last message -> reply")
        for seq in seqs(tag):
            r = load(tag, seq)
            body = r["body"] or {}
            messages = body.get("messages") or []
            last = messages[-1] if messages else {}
            print(f"{seq:>4}  {r['received_at'][11:23]:<12}  {r['body_bytes']:>8,}  {len(messages):>4}  "
                  f"{len(body.get('tools') or []):>5}  {last.get('role', '?')}: "
                  f"{one_line(text_of(last.get('content')), 46)} -> {reply_summary(tag, seq)}")
    elif cmd == "sizes":
        sizes = [(seq, load(tag, seq)["body_bytes"]) for seq in seqs(tag)]
        for seq, size in sizes:
            print(f"{seq:>4}  {size:>9,}")
        if sizes:
            print(f"requests {len(sizes)}, first {sizes[0][1]:,} bytes, largest {max(s for _, s in sizes):,} bytes, "
                  f"all together {sum(s for _, s in sizes):,} bytes")
    elif cmd == "same":
        bodies = [json.dumps(load(tag, int(n))["body"], sort_keys=True) for n in args[1:3]]
        for n, body in zip(args[1:3], bodies):
            print(f"request {n}: {len(body):,} characters, sha256 {hashlib.sha256(body.encode()).hexdigest()}")
        print("the two request bodies are identical" if bodies[0] == bodies[1] else "the two request bodies differ")
    elif cmd == "split":
        groups = {}
        for seq in seqs(tag):
            r = load(tag, seq)
            body = r["body"] or {}
            system = next((text_of(m.get("content")) for m in body.get("messages") or []
                           if m.get("role") in ("system", "developer")), "")
            groups.setdefault(one_line(system, 70), []).append(r["body_bytes"])
        for system, sizes in groups.items():
            print(f"{len(sizes):>4} requests, smallest {min(sizes):>7,}, largest {max(sizes):>7,}, all together "
                  f"{sum(sizes):>10,} bytes | system prompt starts: {system}")
    elif cmd == "searches":
        seen = set()
        for seq in seqs(tag):
            for m in (load(tag, seq)["body"] or {}).get("messages") or []:
                text = text_of(m.get("content"))
                if m.get("role") != "tool" or not text.startswith('{"question"') or text in seen:
                    continue
                seen.add(text)
                answer = json.loads(text)
                print(f"first seen in request {seq}: the tool's answer is {len(text):,} characters. question: {answer['question']}")
                for hit in answer["results"]:
                    print(f"    distance {hit['distance']:.4f}  section {hit['section']:>2}  {hit['title']}  "
                          f"({len(hit['text']):,} characters of text)")
        if not seen:
            print(f"no answer of search_policy in the requests of {tag}")
    elif cmd == "find":
        needle = args[1]
        for seq in seqs(tag):
            body = load(tag, seq)["body"] or {}
            where = [f"message {i} ({m.get('role')})" for i, m in enumerate(body.get("messages") or [])
                     if needle in text_of(m.get("content")) or needle in json.dumps(m.get("tool_calls") or "")]
            where += [f"tool {t['function']['name']}" for t in body.get("tools") or [] if needle in json.dumps(t)]
            if where:
                print(f"{seq:>4}  " + ", ".join(where))
    else:
        r = load(tag, int(args[1]))
        body = r["body"] or {}
        if cmd == "tools":
            tools = body.get("tools") or []
            print(f"request {r['seq']} offers {len(tools)} tools:")
            for t in tools:
                f = t["function"]
                params = ", ".join((f.get("parameters") or {}).get("properties", {}))
                print(f"- {f['name']}({params})" + (f"\n    {one_line(f.get('description', ''), 400)}" if "--full" in args else ""))
        elif cmd == "system":
            for m in body.get("messages") or []:
                if m.get("role") in ("system", "developer"):
                    text = text_of(m.get("content"))
                    print(f"[{m['role']} message, {len(text):,} characters]\n{text}")
        elif cmd == "messages":
            print(f"request {r['seq']}: model {body.get('model')}, {r['body_bytes']:,} bytes, "
                  f"{len(body.get('messages') or [])} messages, {len(body.get('tools') or [])} tools")
            for i, m in enumerate(body.get("messages") or []):
                text = text_of(m.get("content"))
                calls = "".join(f" asks {tc['function']['name']}({tc['function']['arguments']})" for tc in m.get("tool_calls") or [])
                print(f"[{i}] {m.get('role')}{calls} ({len(text):,} characters) {cut(text, limit)!r}")
        elif cmd == "raw":
            print(json.dumps({"path": r["path"], "headers": r["headers"], "body": cut(body, limit)}, indent=2))
        else:
            print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
