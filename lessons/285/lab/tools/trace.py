"""Read traces back from LangSmith's API, to prove what arrived: every call to a model, with its tokens and its cost.

    python -m tools.trace workspace             the plan and the workspace the key belongs to
    python -m tools.trace projects              the workspace's tracing projects, and the agents it has registered
    python -m tools.trace last [N]              the last N traces of the project (default 1): LangSmith's own totals,
                                                and each model call in the trace
    python -m tools.trace calls <trace id>      the model calls of one trace
    python -m tools.trace steps [trace id]      what happened in a trace, in order: each model call and each tool call
                                                with what was asked of it (default: the last trace)
    python -m tools.trace total                 every model call of the project, added up and split by who sent it
    python -m tools.trace prices [text]         the workspace's model price table (entries that hold the text)
    python -m tools.trace nokey                 read every run back and check that none of them holds the key

    --all          a line for every model call, however many there are
    --wait N       wait up to N seconds for a trace that started at or after --since
    --since TIME   only what started at or after this UTC time, such as 2026-11-21T17:30:00Z (default: the last day)
    --until TIME   for last: only traces that started before this UTC time
    --by KEYS      for total: the keys of the calls' metadata to split by, with commas (default lab_agent).
                   lc_agent_name is the name the library gives a helper's calls

It reads LANGSMITH_API_KEY, LANGSMITH_ENDPOINT and LANGSMITH_PROJECT from the environment. It only reads: nothing
here creates or changes anything in LangSmith. A key that can only send traces cannot read them back.
The key is sent in a header and is never printed.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ENDPOINT = (os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com").rstrip("/")
KEY = os.environ.get("LANGSMITH_API_KEY") or ""
PROJECT = os.environ.get("LANGSMITH_PROJECT") or "default"
CALL_FIELDS = ["ID", "NAME", "START_TIME", "STATUS", "METADATA", "PROMPT_TOKENS", "COMPLETION_TOKENS", "TOTAL_TOKENS",
               "PROMPT_COST", "COMPLETION_COST", "TOTAL_COST", "PRICE_MODEL_ID"]
TRACE_FIELDS = ["ID", "NAME", "START_TIME", "END_TIME", "STATUS", "TRACE_ID", "THREAD_ID", "TOTAL_TOKENS", "TOTAL_COST"]


def call(method: str, path: str, body=None, query=None, quiet=False):
    url = ENDPOINT + path + ("?" + urllib.parse.urlencode(query, doseq=True) if query else "")
    request = urllib.request.Request(
        url, method=method, data=None if body is None else json.dumps(body).encode(),
        headers={"X-Api-Key": KEY, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        text = " ".join(error.read().decode(errors="replace").replace(KEY, "[the key]").split())[:400]
        if quiet:
            return {"http_error": error.code, "detail": text}
        sys.exit(f"{method} {path}: HTTP {error.code} {text}")


def items(answer) -> list:
    return answer if isinstance(answer, list) else (answer.get("items") or [])


def project_id() -> str:
    found = items(call("GET", "/api/v2/sessions", query={"name": PROJECT}))
    if not found:
        sys.exit(f"LangSmith has no tracing project named {PROJECT!r} at {ENDPOINT}")
    return found[0]["id"]


def money(value) -> str:
    """Dollars as LangSmith returned them, to a ten-millionth: one call is a small fraction of a cent."""
    return "no cost" if value is None else f"${float(value):.7f}"


def number(value) -> str:
    return "-" if value is None else f"{int(value):,}"


def model_calls(project: str, trace_id: str, since: str) -> list:
    rows, cursor = [], None
    while True:
        body = {"project_ids": [project], "trace_id": trace_id, "run_type": "LLM", "min_start_time": since,
                "page_size": 1000, "selects": CALL_FIELDS, **({"cursor": cursor} if cursor else {})}
        answer = call("POST", "/api/v2/runs/query", body)
        rows += items(answer)
        cursor = answer.get("next_cursor") if isinstance(answer, dict) else None
        if not cursor:
            return sorted(rows, key=lambda r: r.get("start_time") or "")


def show_calls(rows: list, every: bool) -> None:
    print(f"  {'#':>4}  {'started (UTC)':<13} {'model':<22} {'sent by':<16} {'in':>8} {'out':>7}  "
          f"{'in $':>10} {'out $':>10} {'call $':>10}")
    shown = list(enumerate(rows, start=1))
    if not every and len(shown) > 14:
        shown = shown[:6] + [None] + shown[-6:]
    for entry in shown:
        if entry is None:
            print(f"  {'...':>4}  ({len(rows) - 12} more model calls)")
            continue
        n, r = entry
        meta = r.get("metadata") or {}
        print(f"  {n:>4}  {(r.get('start_time') or '')[11:23]:<13} {str(meta.get('ls_model_name', '?'))[:22]:<22} "
              f"{str(meta.get('lab_agent', '-'))[:16]:<16} {number(r.get('prompt_tokens')):>8} "
              f"{number(r.get('completion_tokens')):>7}  {money(r.get('prompt_cost')):>10} "
              f"{money(r.get('completion_cost')):>10} {money(r.get('total_cost')):>10}")
    tokens_in = sum(r.get("prompt_tokens") or 0 for r in rows)
    tokens_out = sum(r.get("completion_tokens") or 0 for r in rows)
    costs = [r.get("total_cost") for r in rows if r.get("total_cost") is not None]
    print(f"  sum of the {len(rows)} model calls: {tokens_in:,} tokens in, {tokens_out:,} out, "
          + (f"${sum(float(c) for c in costs):.7f} ({len(costs)} calls carry a cost)" if costs else "no call carries a cost"))
    labels = {(r.get("metadata") or {}).get("priced_as") for r in rows} - {None}
    for label in labels:
        print(f"  priced_as, from the calls' own metadata: {label}")
    table = {r.get("price_model_id") for r in rows} - {None}
    print("  price table entry used: " + (", ".join(sorted(table)) if table else "none"))


def last(count: int, every: bool, wait: int, since: str | None, until: str | None = None) -> None:
    project = project_id()
    window = since or (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    deadline, before = time.monotonic() + wait, None
    while True:
        traces = items(call("POST", "/api/v2/traces/query", {
            "project_id": project, "min_start_time": window, "page_size": count, "selects": TRACE_FIELDS,
            **({"max_start_time": until} if until else {})}))
        settled = bool(traces) and all(
            str((t.get("root_run") or {}).get("status")).lower() != "pending"
            and (t.get("trace_aggregates") or {}).get("total_tokens") is not None for t in traces[:count])
        calls = [model_calls(project, (t.get("root_run") or {}).get("trace_id") or t["root_run"]["id"], window)
                 for t in traces[:count]] if settled or wait == 0 or time.monotonic() > deadline else None
        seen = None if calls is None else [(len(c), sum(r.get("total_tokens") or 0 for r in c)) for c in calls]
        # LangSmith adds a trace's totals up a little after its runs arrive: wait until they equal the calls' own sum
        whole = seen is not None and all((t.get("trace_aggregates") or {}).get("total_tokens") == tokens
                                         for t, (_, tokens) in zip(traces[:count], seen))
        if wait == 0 or (seen is not None and seen == before and whole):
            break
        if time.monotonic() > deadline:
            break
        before = seen
        time.sleep(3)
    print(f"project {PROJECT} at {ENDPOINT}")
    if not traces:
        print(f"no trace has started since {window}")
        sys.exit(1)
    for trace, rows in zip(traces[:count], calls or [[] for _ in traces]):
        root, sums = trace.get("root_run") or {}, trace.get("trace_aggregates") or {}
        print(f"\ntrace {root.get('trace_id') or root.get('id')}: {root.get('name')}, {root.get('status')}, "
              f"started {root.get('start_time')}" + (f", thread {root['thread_id']}" if root.get("thread_id") else ""))
        print(f"  LangSmith's totals for the trace: {number(sums.get('total_tokens'))} tokens, {money(sums.get('total_cost'))}")
        show_calls(rows, every)


def steps(trace_id: str | None, since: str | None, width: int) -> None:
    """A trace as a list of steps: who called the model, and which tool ran with which arguments."""
    project = project_id()
    window = since or (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    if trace_id is None:
        latest = items(call("POST", "/api/v2/traces/query", {"project_id": project, "min_start_time": window,
                                                             "page_size": 1, "selects": TRACE_FIELDS}))
        if not latest:
            sys.exit(f"no trace has started since {window}")
        root = latest[0].get("root_run") or {}
        trace_id = root.get("trace_id") or root.get("id")
        print(f"trace {trace_id}: {root.get('name')}, {root.get('status')}, started {root.get('start_time')}")
    runs = []
    for kind in ("LLM", "TOOL"):
        runs += all_since("/api/v2/runs/query", {
            "project_ids": [project], "trace_id": trace_id, "run_type": kind, "min_start_time": window, "page_size": 1000,
            "selects": ["ID", "NAME", "RUN_TYPE", "START_TIME", "STATUS", "METADATA", "INPUTS_PREVIEW", "OUTPUTS_PREVIEW",
                        "PROMPT_TOKENS", "COMPLETION_TOKENS", "TOTAL_COST"]})
    for r in sorted(runs, key=lambda r: r.get("start_time") or ""):
        meta = r.get("metadata") or {}
        who = meta.get("lc_agent_name") or meta.get("lab_agent") or "our agent"
        when = (r.get("start_time") or "")[11:19]
        if str(r.get("run_type")).upper() == "LLM":
            print(f"{when}  model call by {who}: {number(r.get('prompt_tokens'))} tokens in, "
                  f"{number(r.get('completion_tokens'))} out, {money(r.get('total_cost'))}")
        else:
            asked = " ".join(str(r.get("inputs_preview") or "").split())
            print(f"{when}    tool {r.get('name')} ({str(r.get('status')).lower()}): {asked[:width]}")
    print(f"{sum(1 for r in runs if str(r.get('run_type')).upper() == 'LLM')} model calls and "
          f"{sum(1 for r in runs if str(r.get('run_type')).upper() == 'TOOL')} tool calls in the trace")


def all_since(path: str, body: dict) -> list:
    rows, cursor = [], None
    while True:
        answer = call("POST", path, {**body, **({"cursor": cursor} if cursor else {})})
        rows += items(answer)
        cursor = answer.get("next_cursor") if isinstance(answer, dict) else None
        if not cursor:
            return rows


def total(since: str | None, by: str, wait: int) -> None:
    """Every model call of the project since a time, added up, and split by one key of the calls' metadata."""
    project = project_id()
    window = since or (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    deadline, before = time.monotonic() + wait, None
    while True:
        calls = all_since("/api/v2/runs/query", {"project_ids": [project], "run_type": "LLM", "min_start_time": window,
                                                 "page_size": 1000, "selects": CALL_FIELDS})
        traces = all_since("/api/v2/traces/query", {"project_id": project, "min_start_time": window, "page_size": 100,
                                                    "selects": TRACE_FIELDS})
        seen = (len(calls), sum(r.get("total_tokens") or 0 for r in calls),
                sum((t.get("trace_aggregates") or {}).get("total_tokens") or 0 for t in traces))
        # done when nothing is still arriving: the same numbers twice, and LangSmith's trace totals equal the calls' sum
        if wait == 0 or (seen == before and seen[1] == seen[2]) or time.monotonic() > deadline:
            break
        before = seen
        time.sleep(4)
    print(f"project {PROJECT} at {ENDPOINT}, since {window}")
    states = {}
    for t in traces:
        state = (t.get("root_run") or {}).get("status")
        states[state] = states.get(state, 0) + 1
    sums = [t.get("trace_aggregates") or {} for t in traces]
    print(f"{len(traces)} traces ({', '.join(f'{n} {s}' for s, n in sorted(states.items(), key=str))}). LangSmith's own totals, "
          f"added up: {sum(s.get('total_tokens') or 0 for s in sums):,} tokens, "
          f"${sum(float(s.get('total_cost') or 0) for s in sums):.7f}")
    groups = {}
    for r in calls:
        key = ", ".join(str((r.get("metadata") or {}).get(k) or "-") for k in by.split(","))
        g = groups.setdefault(key, [0, 0, 0, 0.0, 0, 0])
        g[0] += 1
        g[1] += r.get("prompt_tokens") or 0
        g[2] += r.get("completion_tokens") or 0
        g[3] += float(r.get("total_cost") or 0)
        g[4] += 0 if r.get("total_cost") is None else 1
        g[5] = max(g[5], r.get("prompt_tokens") or 0)
    print(f"\n  {by:<34} {'model calls':>11} {'tokens in':>12} {'tokens out':>11} {'dollars':>13}  {'largest call, tokens in':>23}")
    for key, g in sorted(groups.items()):
        print(f"  {key[:34]:<34} {g[0]:>11,} {g[1]:>12,} {g[2]:>11,} {'$' + format(g[3], '.7f'):>13}  {g[5]:>23,}")
    whole = [sum(g[i] for g in groups.values()) for i in range(5)]
    print(f"  {'all':<34} {whole[0]:>11,} {whole[1]:>12,} {whole[2]:>11,} {'$' + format(whole[3], '.7f'):>13}")
    print(f"\n{whole[4]} of the {whole[0]} model calls carry a cost")
    labels = {(r.get("metadata") or {}).get("priced_as") for r in calls} - {None}
    for label in labels:
        print(f"priced_as, from the calls' own metadata: {label}")


def workspace() -> None:
    """The plan and the workspace the key belongs to. Names and settings only: no identifiers are printed."""
    org = call("GET", "/api/v1/orgs/current")
    config = org.get("config") or {}
    print(f"LangSmith at {ENDPOINT}, version {call('GET', '/api/v1/info').get('version')}")
    print(f"organization: {org.get('display_name')}, personal: {org.get('is_personal')}, plan tier: {org.get('tier')}")
    print(f"a payment method on file: {'yes' if org.get('payment_method') else 'no'}")
    print(f"seats: {config.get('max_identities')}, workspaces allowed: {config.get('max_workspaces')}, "
          f"ready for agents (agent_platform_org_ready): {config.get('agent_platform_org_ready')}")
    for w in items(call("GET", "/api/v1/workspaces")):
        print(f"workspace: {w.get('display_name')}, read only: {w.get('read_only')}")
    limits = call("GET", "/api/v1/workspaces/current/usage_limits", quiet=True)
    if "http_error" not in limits:
        print(f"usage limits set by the owner: {limits.get('tenant_limit')}, traces being refused now: {limits.get('in_reject_set')}")


def no_key(since: str | None) -> None:
    """Read every run of the project back, and look for the key in what LangSmith stored about them."""
    project = project_id()
    window = since or (datetime.now(timezone.utc) - timedelta(days=13)).strftime("%Y-%m-%dT%H:%M:%SZ")
    runs = all_since("/api/v2/runs/query", {"project_ids": [project], "min_start_time": window, "page_size": 1000,
                                            "selects": ["ID", "RUN_TYPE", "METADATA", "EXTRA"]})
    keys, held, kinds = set(), 0, {}
    for r in runs:
        keys |= set((r.get("metadata") or {}).keys())
        kinds[r.get("run_type")] = kinds.get(r.get("run_type"), 0) + 1
        text = json.dumps([r.get("metadata"), r.get("extra")])
        held += (KEY in text) or ("lsv2_" in text)
    print(f"project {PROJECT} at {ENDPOINT}, since {window}")
    print(f"{len(runs):,} runs read back with their metadata and the rest of their extra data: "
          + ", ".join(f"{n:,} {kind}" for kind, n in sorted(kinds.items(), key=str)))
    print(f"runs that hold the key, or any text that starts the way a LangSmith key starts: {held}")
    print("metadata that the SDK took from the environment: " + ", ".join(sorted(k for k in keys if k.isupper())))
    print("every metadata key seen: " + ", ".join(sorted(keys)))
    sys.exit(1 if held else 0)


def prices(text: str) -> None:
    found = items(call("GET", "/api/v1/model-price-map", query={"limit": 100, **({"q": text} if text else {})}))
    print(f"{len(found)} entries" + (f" that hold {text!r}" if text else "") + f" in the price table at {ENDPOINT}")
    print(f"  {'name':<32} {'pattern':<44} {'provider':<10} {'in, $ per 1M':>13} {'out, $ per 1M':>14}  whose")
    for entry in found:
        per_million = [f"{float(entry[k]) * 1_000_000:.4f}" if entry.get(k) is not None else "-"
                       for k in ("prompt_cost", "completion_cost")]
        whose = entry.get("scope") or ("this workspace" if entry.get("tenant_id") else "LangSmith's own")
        print(f"  {str(entry.get('name'))[:32]:<32} {str(entry.get('match_pattern'))[:44]:<44} "
              f"{str(entry.get('provider') or '-')[:10]:<10} {per_million[0]:>13} {per_million[1]:>14}  {whose}")


def main(argv: list) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if not KEY:
        sys.exit("LANGSMITH_API_KEY is not set in this container: start the lab with tools/traced.sh")
    every = "--all" in argv
    wait = int(argv[argv.index("--wait") + 1]) if "--wait" in argv else 0
    since = argv[argv.index("--since") + 1] if "--since" in argv else None
    until = argv[argv.index("--until") + 1] if "--until" in argv else None
    plain = [a for i, a in enumerate(argv)
             if not a.startswith("--") and (i == 0 or argv[i - 1] not in ("--wait", "--since", "--until", "--by", "--width"))]
    command = plain[0]
    if command == "projects":
        found = items(call("GET", "/api/v2/sessions"))
        print(f"{len(found)} tracing projects at {ENDPOINT}")
        for p in found:
            print(f"  {p.get('name')}: first trace {p.get('start_time')}, kept as {p.get('trace_tier')}")
        agents = call("GET", "/api/v1/agents", quiet=True)
        if "http_error" in agents:
            print(f"agents: HTTP {agents['http_error']} (not an agent-based workspace, or the key may not list them)")
        else:
            print(f"{len(items(agents))} agents registered in the workspace")
            for a in items(agents):
                one = call("GET", "/api/v1/agents/" + urllib.parse.quote(a["id"]), quiet=True)
                where = ", ".join(f"{e.get('environment')} -> project {e.get('tracer_session_name')}"
                                  for e in one.get("environments") or [])
                print(f"  {a.get('id')} ({a.get('source_type')}), made {a.get('created_at')}: {where}")
    elif command == "last":
        last(int(plain[1]) if len(plain) > 1 else 1, every, wait, since, until)
    elif command == "calls":
        project = project_id()
        window = since or (datetime.now(timezone.utc) - timedelta(days=13)).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"project {PROJECT} at {ENDPOINT}\n\ntrace {plain[1]}")
        show_calls(model_calls(project, plain[1], window), every)
    elif command == "steps":
        steps(plain[1] if len(plain) > 1 else None, since, int(argv[argv.index("--width") + 1]) if "--width" in argv else 260)
    elif command == "total":
        total(since, argv[argv.index("--by") + 1] if "--by" in argv else "lab_agent", wait)
    elif command == "workspace":
        workspace()
    elif command == "nokey":
        no_key(since)
    elif command == "prices":
        prices(plain[1] if len(plain) > 1 else "")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
