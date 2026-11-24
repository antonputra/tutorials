"""Section 02's last step: a conversation is a list that our program keeps and sends again, whole.

    python -m tools.kept sizes [< request.json]
        How many bytes the first request is, exactly as agent_by_hand.py hands it to the HTTP layer. Nothing is
        sent. With a request body on standard input (as a capture printed it), it also says whether the two are
        the same request.

    python -m tools.kept ask "Which invoice did I just ask about?" < first-reply.json
        One request with the kept list: who the model is, the first question, the text of a reply that came back
        earlier (the JSON of that reply, on standard input), and the new question. It uses the same call the
        hand-written agent makes, and prints the request, the reply, the token counts and what the call costs
        at the lab's price list.
"""
import hashlib
import json
import sys
import urllib.request

import agent_by_hand as hand
from app.pricing import LABEL, cost, usd
from app.prompts import QUESTION, SYSTEM

FIRST = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": QUESTION}]


def as_sent(messages: list) -> tuple[str, bytes]:
    """The address and the body that call_model hands to the HTTP layer for these messages. Nothing leaves."""
    seen = {}

    class NotSent(Exception):
        pass

    def stop(request, *args, **kwargs):
        seen.update(url=request.full_url, body=request.data)
        raise NotSent

    real, urllib.request.urlopen = urllib.request.urlopen, stop
    try:
        hand.call_model(messages)
    except NotSent:
        pass
    finally:
        urllib.request.urlopen = real
    return seen["url"], seen["body"]


def sizes() -> None:
    url, body = as_sent(FIRST)
    print(f"POST {url}")
    print(f"the request body is {len(body):,} bytes, sha256 {hashlib.sha256(body).hexdigest()[:16]}...")
    print("measured as the bytes agent_by_hand.call_model gives to urllib for this request: json.dumps of the model's")
    print("name and the two messages, encoded as UTF-8. The call was stopped there: nothing was sent to a model.")
    print(f"model name {hand.MODEL!r}: {len(hand.MODEL)} characters; first message {len(SYSTEM)} characters; "
          f"second message {len(QUESTION)} characters")
    print(body.decode())
    if not sys.stdin.isatty():
        given = sys.stdin.read().strip()
        if given:
            same = json.loads(given) == json.loads(body)
            print("\nthe request body given on standard input holds " + ("the same model and the same messages: it is this request"
                                                                        if same else "ANOTHER request than this one"))


def ask(question: str) -> None:
    first = json.load(sys.stdin)
    said = first["choices"][0]["message"]["content"]
    kept = FIRST + [{"role": "assistant", "content": said}, {"role": "user", "content": question}]
    body, reply = hand.call_model(kept)
    print(f"POST {hand.BASE_URL}/chat/completions")
    print(f"the request body is {len(json.dumps(body).encode()):,} bytes and holds {len(kept)} messages: the kept list.")
    print("the third message is the text of the earlier reply; its reasoning field is not sent back.\n")
    print(json.dumps(body, indent=2))
    print("\nreply:\n")
    print(json.dumps(reply, indent=2))
    used = reply["usage"]
    spent = sum(cost(used["prompt_tokens"], used["completion_tokens"]))
    print(f"\npriced at: {LABEL}")
    print(f"this call: {used['prompt_tokens']:,} tokens in, {used['completion_tokens']:,} tokens out, {usd(spent)} (computed)")
    before = first.get("usage") or {}
    if before:
        print(f"the earlier reply: {before['prompt_tokens']:,} tokens in, {before['completion_tokens']:,} tokens out, "
              f"{usd(sum(cost(before['prompt_tokens'], before['completion_tokens'])))} (computed)")


if __name__ == "__main__":
    if sys.argv[1:2] == ["sizes"]:
        sizes()
    elif sys.argv[1:2] == ["ask"] and len(sys.argv) > 2:
        ask(sys.argv[2])
    else:
        sys.exit(__doc__)
