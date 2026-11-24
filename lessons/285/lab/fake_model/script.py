"""The scripted stand-in for the model. It is not a model: it is a few rules.

It gets what a model gets: the messages and the tools on offer, and nothing else. It keeps no state
between calls. From the conversation alone it works out the next step, the way the agent loop expects
a model to: ask for one tool, or answer in text. Its answers are computed from the tool results in the
conversation, so a wrong wire (a missing result, a lost message) shows up as a wrong answer.

Which script runs is decided by the last user message and by the tools on offer:
    "... payment run ..."                    walk every invoice due, then pay or hold each one
    "... invoice 1042 ..."                   check one invoice (and "save ... /path.md", "schedule", "one line")
    "... invoices 1055 and 1056 ..."         check several invoices, one after the other
    "Delete the file /path"                  ask for the delete tool once, and report what it answered
    "Remember ...: <rule>"                   add the rule to the memory file with edit_file or write_file
    "... every invoice ... full document"    ask for one very large tool result
    a get_receipts tool on offer             the receiving agent: look up what arrived for a purchase order

Two more rules follow the tools on offer. With search_policy, it looks up who approves payments before the first
payment and writes that into the payment's note. With send_to_receiving and receiving_answer, it sends its question
to the warehouse first, goes on with its own lookups, and reads the answer when it needs it.
"""
import json
import re
from decimal import Decimal

from fake_model import tokens

D = Decimal
CHECK_TASK = ("Check invoice {n} against its purchase order. Reply with one line: "
              "PAY <invoice number> <amount> <short note>, or HOLD <invoice number> <reason>.")
POLICY_NO_PO = "invoice without a purchase order"
POLICY_PARTIAL = "partial delivery: fewer units arrived than the invoice bills"
POLICY_APPROVAL = "approval limits: who approves a payment"


def text_of(content) -> str:
    """Message content is a string, or a list of parts with a text field."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return "".join(p.get("text", "") for p in content if isinstance(p, dict))


def as_json(text):
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def usd(value) -> str:
    return f"${D(str(value)):,.2f}"


def plural(unit: str, n: int) -> str:
    return unit if n == 1 else unit + ("es" if unit.endswith("x") else "s")


class Conversation:
    """What the stand-in can see: the system text, the last user message, and the tool calls after it."""

    def __init__(self, body: dict):
        messages = body.get("messages") or []
        self.tools = {t["function"]["name"]: t["function"] for t in body.get("tools") or []
                      if t.get("type") == "function"}
        self.system = "\n".join(text_of(m.get("content")) for m in messages if m.get("role") in ("system", "developer"))
        users = [i for i, m in enumerate(messages) if m.get("role") == "user"]
        self.user = text_of(messages[users[-1]].get("content")) if users else ""
        self.calls, by_id = [], {}
        for m in messages[(users[-1] + 1) if users else 0:]:
            if m.get("role") == "assistant":
                for tc in m.get("tool_calls") or []:
                    call = {"name": tc["function"]["name"], "args": as_json(tc["function"].get("arguments") or "{}") or {},
                            "result": None}
                    self.calls.append(call)
                    by_id[tc.get("id")] = call
            elif m.get("role") == "tool" and m.get("tool_call_id") in by_id:
                by_id[m["tool_call_id"]]["result"] = text_of(m.get("content"))
        self.calls_ever = sum(len(m.get("tool_calls") or []) for m in messages if m.get("role") == "assistant")

    def result(self, name: str, **args):
        """The first answered call of this turn with this name and these arguments, or None."""
        for call in self.calls:
            if call["name"] == name and call["result"] is not None and "did not complete" not in call["result"] \
                    and all(call["args"].get(k) == v for k, v in args.items()):
                return call
        return None


# ---------------------------------------------------------------- one invoice

def memory_block(system: str) -> str:
    """The text Deep Agents puts between <agent_memory> tags in the system prompt, or nothing."""
    if "<agent_memory>" not in system:
        return ""
    return system.split("<agent_memory>", 1)[1].split("</agent_memory>", 1)[0]


def freight_limit(text: str, supplier: str):
    """A rule such as "Cascade Packaging bills freight ...; pay it when it is $75 or less", if the text has one."""
    for line in text.splitlines():
        if "freight" in line.lower() and supplier.lower() in line.lower():
            m = re.search(r"\$(\d+(?:\.\d+)?)\s+or\s+less", line)
            if m:
                return D(m.group(1))
    return None


def parse_received(answer: str) -> dict:
    """The receiving agent answers in text, one line a product: "- SR-101 Honeycrisp apples: 12 received"."""
    return {m.group(1): int(m.group(2)) for m in re.finditer(r"^- (\S+) .*?: (\d+) received", answer, re.M)}


def assess(inv: dict, po, received, rules_text: str, policy_text: str) -> dict:
    """Compare the invoice with the order and with what arrived. Return the problems, the notes and what to pay."""
    total = D(inv["total_usd"])
    if not inv.get("po_number"):
        reason = f"no purchase order for a total of {usd(total)}"
        hit = (as_json(policy_text) or {}).get("results") or []
        if hit:
            reason += f" (policy section {hit[0]['section']}, {hit[0]['title']})"
        return {"problems": [reason], "notes": [], "pay": None}
    problems, notes, pay = [], [], total
    po_no, po_lines = po["po_number"], {l["sku"]: l for l in po["lines"]}
    for l in inv["lines"]:
        price, qty = D(l["unit_price"]), l["quantity"]
        if l["sku"] == "FREIGHT":
            limit = freight_limit(rules_text, inv["supplier"])
            if limit is not None and price * qty <= limit:
                notes.append(f"freight {usd(price * qty)} is agreed with {inv['supplier']}")
            else:
                problems.append(f"freight line of {usd(price * qty)} is not on {po_no}")
            continue
        ordered = po_lines.get(l["sku"])
        if ordered is None:
            problems.append(f"{l['description']} is not on {po_no}")
            continue
        if qty > ordered["quantity"]:
            problems.append(f"it bills {qty} {plural(l['unit'], qty)} of {l['description']} at {usd(price)}; {po_no} "
                            f"ordered {ordered['quantity']}: overbilled by {usd((qty - ordered['quantity']) * price)}")
        if price != D(ordered["unit_price"]):
            problems.append(f"unit price {usd(price)} for {l['description']}; {po_no} says {usd(ordered['unit_price'])}: "
                            f"overbilled by {usd((price - D(ordered['unit_price'])) * qty)}")
    earlier = [v for v in po.get("invoices", []) if v["invoice_number"] < inv["invoice_number"]
               and D(v["total_usd"]) == total]
    if earlier:
        problems.append(f"duplicate of invoice {earlier[0]['invoice_number']}: same supplier, {po_no} and {usd(total)}")
    for l in inv["lines"]:
        got = (received or {}).get(l["sku"])
        if got is not None and got < l["quantity"]:
            short = (l["quantity"] - got) * D(l["unit_price"])
            what = f"only {got} of {l['quantity']} {plural(l['unit'], l['quantity'])} of {l['description']} arrived"
            if "pay only for the units received" in policy_text:
                pay -= short
                notes.append(f"{what}: short-paid by {usd(short)}")
            else:
                problems.append(what)
    return {"problems": problems, "notes": notes, "pay": None if problems else pay}


def work_invoice(c: Conversation, n: int):
    """The next lookup for invoice n as ("call", name, args), or ("done", invoice, verdict)."""
    rules = c.system + "\n" + c.user
    told = re.search(r"Read (/memories/\S+?\.md) first", c.user)      # a helper told to read the memory file itself
    if told and "read_file" in c.tools:
        r = c.result("read_file", file_path=told.group(1))
        if r is None:
            return "call", "read_file", {"file_path": told.group(1)}
        rules += "\n" + r["result"]
    r = c.result("get_invoice", invoice_number=n)
    if r is None:
        return "call", "get_invoice", {"invoice_number": n}
    inv = as_json(r["result"])
    if inv is None or "error" in inv:
        return "done", None, {"problems": [f"could not be read: {r['result'][:200]}"], "notes": [], "pay": None}
    po = received = None
    need = None
    if inv.get("po_number"):
        sent = None
        if "send_to_receiving" in c.tools:      # do not wait: send the question now, read the answer when it is needed
            sent = c.result("send_to_receiving", po_number=inv["po_number"])
            if sent is None:
                return "call", "send_to_receiving", {"po_number": inv["po_number"]}
        r = c.result("get_purchase_order", po_number=inv["po_number"])
        if r is None:
            return "call", "get_purchase_order", {"po_number": inv["po_number"]}
        po = as_json(r["result"])
        if sent is not None:
            task_id = (as_json(sent["result"]) or {}).get("task_id")
            r = c.result("receiving_answer", task_id=task_id)
            if r is None:
                return "call", "receiving_answer", {"task_id": task_id}
            received = parse_received((as_json(r["result"]) or {}).get("answer") or "")
        elif "ask_receiving" in c.tools:
            r = c.result("ask_receiving", po_number=inv["po_number"])
            if r is None:
                return "call", "ask_receiving", {"po_number": inv["po_number"]}
            received = parse_received(r["result"])
        if received is not None and any(received.get(l["sku"], l["quantity"]) < l["quantity"] for l in inv["lines"]):
            need = POLICY_PARTIAL
    else:
        need = POLICY_NO_PO
    policy = ""
    if need and "search_policy" in c.tools:
        r = c.result("search_policy", question=need)
        if r is None:
            return "call", "search_policy", {"question": need}
        policy = r["result"]
    return "done", inv, assess(inv, po, received, rules, policy)


def finding(n: int, inv, verdict: dict) -> str:
    if inv is None:
        return f"Invoice {n} {verdict['problems'][0]}"
    where = inv.get("po_number") or "any purchase order"
    if verdict["problems"]:
        return f"Invoice {n} from {inv['supplier']} does not match {where}: " + "; ".join(verdict["problems"]) + "."
    notes = (" Notes: " + "; ".join(verdict["notes"]) + ".") if verdict["notes"] else ""
    return (f"Invoice {n} from {inv['supplier']} matches {where}: {len(inv['lines'])} lines, "
            f"pay {usd(verdict['pay'])}.{notes}")


def approvers(c: Conversation, amount):
    """Who else has to approve a payment of this amount, read from the policy: ("call", ...) or ("note", text)."""
    if "search_policy" not in c.tools:
        return "note", ""
    r = c.result("search_policy", question=POLICY_APPROVAL)
    if r is None:
        return "call", "search_policy", {"question": POLICY_APPROVAL}
    found = []
    for hit in (as_json(r["result"]) or {}).get("results") or []:
        for m in re.finditer(r"A payment above \$([\d,]+) (?:also )?needs the ([a-z ]+?)\.", hit["text"]):
            if D(str(amount)) > D(m.group(1).replace(",", "")):
                found.append(f"over ${m.group(1)}: the {m.group(2)} also approves "
                             f"(policy section {hit['section']}, {hit['title']})")
    return "note", "; ".join(found)


def pay_or_hold(c: Conversation, n: int, inv, verdict: dict):
    """The write step for one checked invoice: ("call", ...) while it is still to do, else ("did", text)."""
    if verdict["problems"]:
        r = c.result("hold_invoice", invoice_number=n)
        if r is None:
            return "call", "hold_invoice", {"invoice_number": n, "reason": "; ".join(verdict["problems"])}
        return "did", f"Invoice {n} is on hold: {'; '.join(verdict['problems'])}."
    r = c.result("schedule_payment", invoice_number=n)
    if r is None:
        who = approvers(c, verdict["pay"])
        if who[0] == "call":
            return who
        note = "; ".join([f"{inv['supplier']}, {inv['po_number']}"] + verdict["notes"] + ([who[1]] if who[1] else []))
        return "call", "schedule_payment", {"invoice_number": n, "amount_usd": float(verdict["pay"]), "note": note}
    # After a person edits the call, the harness puts a note in front of the tool's own answer.
    paid = as_json(r["result"]) or as_json(r["result"].split("Tool response:", 1)[-1].strip())
    if paid is None or "payment_id" not in paid:
        return "did", f"Invoice {n} matches {inv['po_number']}, but no payment was scheduled: {r['result']}"
    return "did", (f"Invoice {n} matches {inv['po_number']}. A payment of {usd(paid['amount_usd'])} is scheduled for "
                   f"{paid['pay_date']} (payment {paid['payment_id']}).")


def one_invoice(c: Conversation, n: int):
    if not c.tools:
        return "text", (f"[scripted reply] I cannot see invoice {n}. No tool was offered, so I have no way to read it. "
                        "A real model may answer anyway, and it would be guessing.")
    step = work_invoice(c, n)
    if step[0] == "call":
        return step
    _, inv, verdict = step
    low = (c.system + "\n" + c.user).lower()
    if "one line" in low:
        if verdict["problems"]:
            return "text", f"HOLD {n} " + "; ".join(verdict["problems"])
        return "text", f"PAY {n} {verdict['pay']:.2f} " + "; ".join([f"{inv['supplier']}, {inv['po_number']}"] + verdict["notes"])
    text = finding(n, inv, verdict)
    save = re.search(r"(/[A-Za-z0-9_./-]+\.md)", c.user)
    if save and "save" in c.user.lower() and "write_file" in c.tools and c.result("write_file", file_path=save.group(1)) is None:
        return "call", "write_file", {"file_path": save.group(1), "content": text + "\n"}
    if re.search(r"\b(schedule|pay)\b", c.user.lower()) and "schedule_payment" in c.tools and inv is not None:
        step = pay_or_hold(c, n, inv, verdict)
        if step[0] == "call":
            return step
        text = step[1]
    if save and c.result("write_file", file_path=save.group(1)):
        text += f" Saved to {save.group(1)}."
    return "text", text


def several_invoices(c: Conversation, numbers: list):
    """Check a few invoices in one conversation. With the send-and-read-later tools, every question goes to the
    warehouse before the first purchase order is read, so the warehouse works while we do."""
    if "send_to_receiving" in c.tools:
        for n in numbers:
            r = c.result("get_invoice", invoice_number=n)
            if r is None:
                return "call", "get_invoice", {"invoice_number": n}
            po = (as_json(r["result"]) or {}).get("po_number")
            if po and c.result("send_to_receiving", po_number=po) is None:
                return "call", "send_to_receiving", {"po_number": po}
    lines = []
    for n in numbers:
        step = work_invoice(c, n)
        if step[0] == "call":
            return step
        lines.append(finding(n, step[1], step[2]))
    return "text", "\n".join(lines)


# ---------------------------------------------------------------- the payment run

def payment_run(c: Conversation):
    due = (re.search(r"\d{4}-\d{2}-\d{2}", c.user) or re.search(r"2026-11-27", "2026-11-27")).group(0)
    r = c.result("list_invoices_due")
    if r is None:
        return "call", "list_invoices_due", {"due_date": due}
    listed = as_json(r["result"])
    if listed is None:
        return "text", f"The list of invoices could not be read: {r['result'][:300]}"
    delegate = "task" in c.tools and "invoice-checker" in c.tools["task"].get("description", "")
    rules = " ".join(l.strip()[2:] for l in memory_block(c.system).splitlines() if l.strip().startswith("- "))
    paid, held, failed = [], [], []
    for row in listed["invoices"]:
        n = row["invoice_number"]
        done_pay, done_hold = c.result("schedule_payment", invoice_number=n), c.result("hold_invoice", invoice_number=n)
        if done_hold:
            held.append((n, done_hold["args"].get("reason", "")))
            continue
        if done_pay:
            ok = as_json(done_pay["result"])
            if ok and "payment_id" in ok:
                paid.append((n, D(str(ok["amount_usd"]))))
            else:
                failed.append((n, done_pay["result"]))
            continue
        if delegate:
            # A helper starts with a clean page: it knows only what this task text tells it.
            if "read /memories/agents.md first" in c.user.lower():
                task = CHECK_TASK.format(n=n) + " Read /memories/AGENTS.md first: it holds the supplier rules we know."
            else:
                task = CHECK_TASK.format(n=n) + (f" Supplier rules we know: {rules}" if rules else "")
            answer = next((x for x in c.calls if x["name"] == "task" and x["result"] is not None
                           and x["args"].get("description", "").startswith(f"Check invoice {n} ")), None)
            if answer is None:
                return "call", "task", {"description": task, "subagent_type": "invoice-checker"}
            m = re.match(r"\s*(PAY|HOLD) (\d+) (.*)", answer["result"], re.S)
            if m and m.group(1) == "PAY":
                amount, _, note = m.group(3).partition(" ")
                who = approvers(c, amount)
                if who[0] == "call":
                    return who
                note = "; ".join([note] + ([who[1]] if who[1] else []))
                return "call", "schedule_payment", {"invoice_number": n, "amount_usd": float(amount), "note": note}
            reason = m.group(3).strip() if m else f"the checker gave no verdict: {answer['result'][:200]}"
            return "call", "hold_invoice", {"invoice_number": n, "reason": reason}
        step = work_invoice(c, n)
        if step[0] == "call":
            return step
        return pay_or_hold(c, n, step[1], step[2])
    lines = [f"Payment run for invoices due {due}: {len(listed['invoices'])} invoices checked.",
             f"Scheduled {len(paid)} payments, {usd(sum((a for _, a in paid), D('0')))} in total.",
             f"Put {len(held)} invoices on hold:"]
    lines += [f"- {n}: {reason}" for n, reason in held]
    if failed:
        lines.append(f"{len(failed)} payments were not scheduled:")
        lines += [f"- {n}: {why}" for n, why in failed]
    return "text", "\n".join(lines)


# ---------------------------------------------------------------- memory, a large result, the receiving agent

def remember(c: Conversation):
    rule = c.user.split(":", 1)[1].strip() if ":" in c.user else c.user.strip()
    path = (re.search(r"<agent_memory>\s*(/\S+)", c.system) or re.search(r"(/memories/AGENTS\.md)", "/memories/AGENTS.md")).group(1)
    done = c.result("edit_file", file_path=path) or c.result("write_file", file_path=path)
    if done:
        if done["result"].startswith("Error"):      # the tool refused: say so, never "saved"
            return "text", f"Not saved. The file tool answered: {done['result']}"
        return "text", f"Saved to {path}: {rule}"
    memory = memory_block(c.system)
    body = [l for l in memory.splitlines() if l.strip() and l.strip() != path]
    if not body or "(No memory loaded)" in memory:
        return "call", "write_file", {"file_path": path, "content": f"# What the payables agent has learned\n\n- {rule}\n"}
    return "call", "edit_file", {"file_path": path, "old_string": body[-1], "new_string": f"{body[-1]}\n- {rule}"}


def large_result(c: Conversation):
    due = (re.search(r"\d{4}-\d{2}-\d{2}", c.user) or re.search(r"2026-11-27", "2026-11-27")).group(0)
    r = c.result("list_invoices_due")
    if r is None:
        return "call", "list_invoices_due", {"due_date": due, "include_documents": True}
    saved = re.search(r"saved in the filesystem at this path: (\S+)", r["result"])
    if not saved:
        return "text", f"The tool result arrived whole: {len(r['result'])} characters in one message."
    if c.result("read_file", file_path=saved.group(1)) is None:
        return "call", "read_file", {"file_path": saved.group(1), "offset": 0, "limit": 5}
    return "text", (f"The tool result was too large for the conversation. The harness saved it to {saved.group(1)} "
                    "and showed me a preview. I read its first 5 lines with read_file.")


def delete_file(c: Conversation):
    path = re.search(r"(/[\w/-]+(?:\.\w+)?)", c.user)
    if not path or "delete" not in c.tools:
        return "text", "[scripted reply] Tell me which file to delete, and offer me the delete tool."
    r = c.result("delete", file_path=path.group(1))
    if r is None:
        return "call", "delete", {"file_path": path.group(1)}
    return "text", f"I asked for delete on {path.group(1)}. The tool answered: {r['result']}"


def receiving(c: Conversation):
    po = re.search(r"PO-\d+", c.user)
    if not po:
        return "text", "Tell me the purchase order number, for example PO-2207."
    r = c.result("get_receipts", po_number=po.group(0))
    if r is None:
        return "call", "get_receipts", {"po_number": po.group(0)}
    data = as_json(r["result"]) or {}
    if not data.get("receipts"):
        return "text", f"{po.group(0)}: nothing has been received."
    out = []
    for rec in data["receipts"]:
        out.append(f"{po.group(0)}: received on {rec['received_date']} at {rec['dock']} by {rec['received_by']}.")
        out += [f"- {l['sku']} {l['description']}: {l['quantity_received']} received" for l in rec["lines"]]
    return "text", "\n".join(out)


# ---------------------------------------------------------------- the entry point

def next_step(body: dict):
    c = Conversation(body)
    low = c.user.lower()
    one = re.search(r"invoice\s+#?(\d{4})\b", low)
    several = re.search(r"invoices\s+\d{4}(?:\s*(?:,|and)\s*\d{4})+", low)
    if "get_receipts" in c.tools:
        step = receiving(c)
    elif "payment run" in low:
        step = payment_run(c)
    elif low.startswith("remember"):
        step = remember(c)
    elif low.startswith("delete"):
        step = delete_file(c)
    elif several:
        step = several_invoices(c, [int(n) for n in re.findall(r"\d{4}", several.group(0))])
    elif "every invoice" in low and "full document" in low:
        step = large_result(c)
    elif one:
        step = one_invoice(c, int(one.group(1)))
    else:
        step = "text", "[scripted reply] I am a scripted stand-in for a model. Ask me about an invoice or a payment run."
    return c, step


def reply(body: dict) -> dict:
    """A Chat Completions reply for this request."""
    c, step = next_step(body)
    if step[0] == "call":
        message = {"role": "assistant", "content": None, "tool_calls": [{
            "id": f"call_{c.calls_ever + 1:04d}", "type": "function",
            "function": {"name": step[1], "arguments": json.dumps(step[2])}}]}
        finish = "tool_calls"
    else:
        message = {"role": "assistant", "content": step[1]}
        finish = "stop"
    # The stand-in has no tokenizer of its own. The counts come from an open-source one: fake_model/tokens.py.
    return {"object": "chat.completion", "model": body.get("model", "scripted-1"),
            "choices": [{"index": 0, "message": message, "finish_reason": finish}],
            "usage": tokens.usage(body, message)}
