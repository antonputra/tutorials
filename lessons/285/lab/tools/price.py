"""What tokens cost at the lab's price list (price-list.json). The lab's own models are free: this is what the same
tokens would cost at the hosted model the list names, on the day the list was read.

    python -m tools.price 59 350             one call: tokens in, tokens out
    python -m tools.price hand ["question"]  run the hand-written agent's loop, and price each of its requests
    python -m tools.price log <tag>          every request in one folder of the scripted model's log, and the sum
    python -m tools.price log <tag> --all    the same, with a line for each request

The hand-written agent uses no library, so nothing traces it: its price is computed here, from the token counts
in the model's own replies.
"""
import json
import sys
from pathlib import Path

from app.pricing import LABEL, PER_CACHED_INPUT_TOKEN, PRICES, cost, usd

LOG = Path("/logs")


def both(tokens_in: int, tokens_out: int):
    return sum(cost(tokens_in, tokens_out))


def one(tokens_in: int, tokens_out: int) -> None:
    spent_in, spent_out = cost(tokens_in, tokens_out)
    total = spent_in + spent_out
    print(f"priced at: {LABEL}")
    print(f"{tokens_in:>7,} tokens in   {usd(spent_in)}")
    print(f"{tokens_out:>7,} tokens out  {usd(spent_out)}")
    print(f"this call            {usd(total)}, which is {total * 100:.5f} cents"
          + (f": about 1/{round(1 / (total * 100))} of a cent" if 0 < total < 1 / 100 else ""))


def hand(question: str | None) -> None:
    """The hand-written loop, unchanged, with one thing added from outside: each reply's token counts are kept."""
    import agent_by_hand
    from app.prompts import QUESTION

    calls, real_call = [], agent_by_hand.call_model

    def counted(messages, tools=None):
        body, reply = real_call(messages, tools)
        calls.append((len(json.dumps(body).encode()), reply["usage"]["prompt_tokens"], reply["usage"]["completion_tokens"]))
        return body, reply

    agent_by_hand.call_model = counted
    messages = agent_by_hand.run_agent(question or QUESTION)
    print(f"model {agent_by_hand.MODEL}: {len(calls)} requests, {sum(1 for m in messages if m['role'] == 'tool')} tool calls")
    print(f"priced at: {LABEL}")
    print(f"{'request':>7}  {'bytes':>9}  {'tokens in':>9}  {'tokens out':>10}  {'dollars':>12}")
    for n, (size, tokens_in, tokens_out) in enumerate(calls, start=1):
        print(f"{n:>7}  {size:>9,}  {tokens_in:>9,}  {tokens_out:>10,}  {usd(both(tokens_in, tokens_out)):>12}")
    all_in, all_out = sum(c[1] for c in calls), sum(c[2] for c in calls)
    print(f"{'all':>7}  {sum(c[0] for c in calls):>9,}  {all_in:>9,}  {all_out:>10,}  {usd(both(all_in, all_out)):>12}")
    print()
    for m in messages:      # the conversation, as agent_by_hand.py prints it
        if m["role"] == "assistant" and m.get("tool_calls"):
            if (m.get("content") or "").strip():
                print(f"model says   {' '.join(m['content'].split())}")
            for call in m["tool_calls"]:
                print(f"model asks   {call['function']['name']}({call['function']['arguments']})")
        elif m["role"] == "tool":
            print(f"we answer    {len(m['content']):,} characters: {m['content'][:110]}...")
        else:
            print(f"{m['role']:<12} {m['content']}")


def sender(request: dict) -> str:
    """Who sent a request: the lab's agents name themselves in a header, and a helper has its own instructions."""
    who = request["headers"].get("x-lab-agent")
    if who is None:
        return "by hand"
    system = next((m.get("content") for m in (request["body"] or {}).get("messages") or [] if m.get("role") == "system"), "")
    system = system if isinstance(system, str) else "".join(p.get("text", "") for p in system if isinstance(p, dict))
    if who == "payables-agent":
        return "a helper" if system.startswith("You check one supplier invoice") else "our agent"
    return "the receiving agent" if who == "receiving-agent" else who


def log(tag: str, every: bool) -> None:
    rows = []
    for path in sorted((LOG / tag).glob("[0-9][0-9][0-9][0-9].reply.json")):
        seq = int(path.name[:4])
        reply = json.loads(path.read_text())
        if reply.get("status") != 200:
            continue
        request = json.loads((LOG / tag / f"{seq:04d}.request.json").read_text())
        used = reply["reply"]["usage"]
        rows.append((seq, sender(request), request["body_bytes"], used["prompt_tokens"], used["completion_tokens"]))
    if not rows:
        sys.exit(f"no replies in {LOG / tag}")
    print(f"scripted model, request log {tag}")
    print(f"priced at: {LABEL}")
    print(f"{'request':>7}  {'sent by':<20} {'bytes':>9}  {'tokens in':>9}  {'tokens out':>10}  {'dollars':>12}")
    shown = rows if every or len(rows) <= 12 else rows[:5] + [None] + rows[-5:]
    for row in shown:
        if row is None:
            print(f"{'...':>7}  ({len(rows) - 10} more requests)")
            continue
        seq, who, size, tokens_in, tokens_out = row
        print(f"{seq:>7}  {who:<20} {size:>9,}  {tokens_in:>9,}  {tokens_out:>10,}  {usd(both(tokens_in, tokens_out)):>12}")
    senders = {}
    for _, who, size, tokens_in, tokens_out in rows:
        entry = senders.setdefault(who, [0, 0, 0, 0, 0])
        entry[0] += 1
        entry[1] += tokens_in
        entry[2] += tokens_out
        entry[3] += size
        entry[4] = max(entry[4], tokens_in)
    print()
    for who, (requests, tokens_in, tokens_out, size, largest) in senders.items():
        print(f"{who}: {requests} requests, {size:,} bytes, {tokens_in:,} tokens in, {tokens_out:,} tokens out, "
              f"{usd(both(tokens_in, tokens_out))}; its largest request is {largest:,} tokens")
    all_in, all_out = sum(r[3] for r in rows), sum(r[4] for r in rows)
    largest = max(rows, key=lambda r: r[3])
    print(f"all {len(rows)} requests: {sum(r[2] for r in rows):,} bytes, {all_in:,} tokens in, {all_out:,} tokens out, "
          f"{usd(both(all_in, all_out))}")
    print(f"the first request {usd(both(rows[0][3], rows[0][4]))}, the last {usd(both(rows[-1][3], rows[-1][4]))}; "
          f"the largest is request {largest[0]}: {largest[2]:,} bytes, {largest[3]:,} tokens in")
    floor = all_in * PER_CACHED_INPUT_TOKEN + cost(0, all_out)[1]
    print(f"input is {100 * both(all_in, 0) / both(all_in, all_out):.1f} % of that sum. A provider bills input it has "
          f"seen before at a lower price: with every input token at the list's cached-input price, "
          f"${PRICES['usd_per_million_cached_input_tokens']} per 1M, the sum would be {usd(floor)}. A real bill lies between the two.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "log":
        log(args[1], "--all" in args)
    elif args[:1] == ["hand"]:
        hand(args[1] if len(args) > 1 else None)
    elif len(args) == 2 and all(a.isdigit() for a in args):
        one(int(args[0]), int(args[1]))
    else:
        sys.exit(__doc__)
