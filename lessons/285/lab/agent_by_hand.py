"""An AI agent by hand. Standard library only: one HTTP call, two tools, and a loop.

    python agent_by_hand.py one     one request to the model, no tools
    python agent_by_hand.py offer   the same request with tools on offer: the model asks, nothing runs
    python agent_by_hand.py loop    the agent: call the model, run the tool it asks for, send the result back, repeat

A question of your own goes last: python agent_by_hand.py loop "Is invoice 1031 correct?"
"""
import json
import os
import sys
import urllib.request

from app.payables import get_invoice, get_purchase_order    # plain functions that read the database
from app.prompts import QUESTION, SYSTEM                     # the system prompt and the question, as text

BASE_URL = os.environ["MODEL_BASE_URL"]     # any endpoint that speaks the OpenAI-compatible Chat Completions API
MODEL = os.environ["MODEL_NAME"]
API_KEY = os.environ["MODEL_API_KEY"]

TOOLS = {"get_invoice": get_invoice, "get_purchase_order": get_purchase_order}
TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_invoice",
        "description": "Get one supplier invoice: supplier, purchase order number, lines, total and the text of the paper invoice.",
        "parameters": {"type": "object", "properties": {"invoice_number": {"type": "integer"}},
                       "required": ["invoice_number"]}}},
    {"type": "function", "function": {
        "name": "get_purchase_order",
        "description": "Get one purchase order: what Juniper Market ordered, at what price, and the invoices billed against it.",
        "parameters": {"type": "object", "properties": {"po_number": {"type": "string"}},
                       "required": ["po_number"]}}},
]


def call_model(messages, tools=None):
    """One HTTP request to the model, one reply. This is everything a model does."""
    body = {"model": MODEL, "messages": messages}
    if tools:
        body["tools"] = tools
    request = urllib.request.Request(
        BASE_URL + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + API_KEY})
    with urllib.request.urlopen(request) as response:
        return body, json.load(response)


def run_agent(question):
    # --- the loop starts
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    while True:
        _, reply = call_model(messages, TOOL_SCHEMAS)
        message = reply["choices"][0]["message"]
        messages.append(message)
        if not message.get("tool_calls"):
            return messages
        for call in message["tool_calls"]:
            function = TOOLS[call["function"]["name"]]
            arguments = json.loads(call["function"]["arguments"])
            result = function(**arguments)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    # --- the loop ends


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "loop"
    question = sys.argv[2] if len(sys.argv) > 2 else QUESTION
    start = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    if mode in ("one", "offer"):
        body, reply = call_model(start, TOOL_SCHEMAS if mode == "offer" else None)
        print(f"POST {BASE_URL}/chat/completions\n")
        print(json.dumps(body, indent=2))
        print("\nreply:\n")
        print(json.dumps(reply, indent=2))
        return
    messages = run_agent(question)
    for m in messages:
        if m["role"] == "assistant" and m.get("tool_calls"):
            for call in m["tool_calls"]:
                print(f"model asks   {call['function']['name']}({call['function']['arguments']})")
        elif m["role"] == "tool":
            print(f"we answer    {len(m['content']):,} characters: {m['content'][:110]}...")
        else:
            print(f"{m['role']:<12} {m['content']}")
    calls = sum(1 for m in messages if m["role"] == "assistant")
    print(f"\n{calls} requests to the model, {sum(1 for m in messages if m['role'] == 'tool')} tool calls run by our code")


if __name__ == "__main__":
    main()
