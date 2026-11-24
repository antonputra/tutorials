"""The hand-written agent with its list kept in Postgres: the same loop, and ten lines that save and load.

    python agent_by_hand_saved.py <run name> [ms]   the Friday payment run. Started again with the same name, it
                                                    reads its list back and carries on.

After every turn (the model's reply and the results of the tools it asked for) the whole list is written to
one row. That is all it knows: the list. It does not know which step it was in when it died, so it repeats
the turn it was in, the request to the model and the tool call after it.
"""
import json
import os
import sys

import psycopg

from agent_by_hand import TOOL_SCHEMAS, call_model     # the same HTTP call and the two tool descriptions
from app.control import begin
from app.payables import TOOLS                          # all five plain functions
from app.prompts import PAYMENT_RUN, SYSTEM

DB = os.environ["AGENT_DB_URL"]
MORE_SCHEMAS = [                                        # the three other tools, described by hand like the first two
    {"type": "function", "function": {
        "name": "list_invoices_due",
        "description": "List the invoices due on a date (YYYY-MM-DD): number, supplier, purchase order number and total.",
        "parameters": {"type": "object", "properties": {"due_date": {"type": "string"}}, "required": ["due_date"]}}},
    {"type": "function", "function": {
        "name": "hold_invoice",
        "description": "Put an invoice on hold so it is not paid, and record the reason.",
        "parameters": {"type": "object", "properties": {"invoice_number": {"type": "integer"}, "reason": {"type": "string"}},
                       "required": ["invoice_number", "reason"]}}},
    {"type": "function", "function": {
        "name": "schedule_payment",
        "description": "Schedule the payment of an invoice for its due date. This moves money: it writes a row in payments.",
        "parameters": {"type": "object", "properties": {"invoice_number": {"type": "integer"},
                                                        "amount_usd": {"type": "number"}, "note": {"type": "string"}},
                       "required": ["invoice_number", "amount_usd", "note"]}}},
]


# --- save and load start
def load(run):
    with psycopg.connect(DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS lists (run text PRIMARY KEY, messages jsonb NOT NULL, saves integer NOT NULL)")
        row = db.execute("SELECT messages FROM lists WHERE run = %s", (run,)).fetchone()
    return row[0] if row else None


def save(run, messages):
    with psycopg.connect(DB) as db:
        db.execute("INSERT INTO lists VALUES (%s, %s, 1) ON CONFLICT (run) DO UPDATE"
                   " SET messages = EXCLUDED.messages, saves = lists.saves + 1", (run, json.dumps(messages)))
# --- save and load end


def run_agent(run, task):
    messages = load(run)                                # the list as it was after the last finished turn, or nothing
    print(f"run {run}: " + (f"{len(messages)} messages read back from Postgres, carrying on" if messages
                            else "nothing saved yet, starting"), flush=True)
    messages = messages or [{"role": "system", "content": SYSTEM}, {"role": "user", "content": task}]
    while True:
        _, reply = call_model(messages, TOOL_SCHEMAS + MORE_SCHEMAS)
        message = reply["choices"][0]["message"]
        messages.append(message)
        for call in message.get("tool_calls") or []:
            result = TOOLS[call["function"]["name"]](**json.loads(call["function"]["arguments"]))
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
        save(run, messages)                             # one turn is finished: write the whole list
        if not message.get("tool_calls"):
            return messages


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    begin(f"s2-saved-{sys.argv[1]}", int(sys.argv[2]) if len(sys.argv) > 2 else 0, fresh=False)
    done = run_agent(sys.argv[1], PAYMENT_RUN)
    print(f"{sum(1 for m in done if m['role'] == 'assistant')} replies from the model in the list, "
          f"{sum(1 for m in done if m['role'] == 'tool')} tool results, {len(done)} messages\n")
    print(done[-1]["content"])
