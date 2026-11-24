"""Do the scripted model's token counts reach LangChain? One short run, and three numbers for each request.

    python -m tools.usage

For every request of the run it prints what the scripted model's reply said it used (read from its own log),
what LangChain holds on the message it built from that reply, and a fresh count of the logged request made
here with the same open-source tokenizer. The three must be equal.
"""
import json
import sys
from pathlib import Path

from langchain.agents import create_agent

from app.common import get_invoice, get_purchase_order, make_model
from app.control import begin
from app.prompts import QUESTION, SYSTEM
from fake_model import tokens

TAG = "usage-proof"
LOG = Path("/logs") / TAG


def main() -> None:
    begin(TAG)
    agent = create_agent(model=make_model(), tools=[get_invoice, get_purchase_order], system_prompt=SYSTEM)
    result = agent.invoke({"messages": [{"role": "user", "content": QUESTION}]})
    replies = [m for m in result["messages"] if m.type == "ai"]
    print(f"tokenizer: tiktoken, encoding {tokens.ENCODING}\n")
    print(f"{'request':>7}  {'the reply said':<22} {'LangChain holds':<22} {'counted again':<22}")
    ok = True
    for seq, message in enumerate(replies, start=1):
        request = json.loads((LOG / f"{seq:04d}.request.json").read_text())["body"]
        reply = json.loads((LOG / f"{seq:04d}.reply.json").read_text())["reply"]
        said = (reply["usage"]["prompt_tokens"], reply["usage"]["completion_tokens"])
        held = (message.usage_metadata["input_tokens"], message.usage_metadata["output_tokens"])
        again = tokens.usage(request, reply["choices"][0]["message"])
        again = (again["prompt_tokens"], again["completion_tokens"])
        same = said == held == again
        ok = ok and same
        cells = [f"{a:,} in, {b:,} out" for a, b in (said, held, again)]
        print(f"{seq:>7}  {cells[0]:<22} {cells[1]:<22} {cells[2]:<22} {'equal' if same else 'DIFFERENT'}")
    last = replies[-1]
    print(f"\nthe last message's usage_metadata, as LangChain holds it:\n{json.dumps(last.usage_metadata, indent=2)}")
    print(f"its response_metadata token_usage:\n{json.dumps(last.response_metadata.get('token_usage'), indent=2)}")
    print(f"\n{len(replies)} requests, " + ("every count equal in all three places" if ok else "NOT every count equal"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
