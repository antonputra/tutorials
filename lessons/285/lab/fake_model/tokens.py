"""Token counts for the scripted model's replies.

The stand-in is not a model, so it has no tokenizer of its own. It counts with an open-source one:
tiktoken (MIT license), encoding o200k_base. The image holds the encoding's vocabulary file, so
counting needs no network.

    input    3 tokens for each message and 3 for the reply's start, plus the tokens of each message's
             role, its text, and the name and arguments of each tool call it holds, plus the tokens of
             the tool descriptions as JSON
    output   the tokens of the reply's text, or of the tool call's name and arguments

A hosted model counts with its own tokenizer and its own hidden format for messages and tools. Its
numbers for the same request are near these, not equal to them.
"""
import json
from functools import lru_cache

import tiktoken

ENCODING = "o200k_base"
PER_MESSAGE = 3
REPLY_START = 3
_encoding = tiktoken.get_encoding(ENCODING)


@lru_cache(maxsize=8192)
def count(text: str) -> int:
    """How many tokens a text is. Remembered: a conversation sends the same messages again with every request."""
    return len(_encoding.encode(text, disallowed_special=())) if text else 0


def _text(content) -> str:
    """Message content is a string, or a list of parts with a text field."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content if isinstance(part, dict))


def _calls(message: dict) -> int:
    total = 0
    for call in message.get("tool_calls") or []:
        function = call.get("function") or {}
        total += count(function.get("name") or "") + count(function.get("arguments") or "")
    return total


def message_tokens(message: dict) -> int:
    return PER_MESSAGE + count(message.get("role") or "") + count(_text(message.get("content"))) + _calls(message)


def usage(body: dict, reply_message: dict) -> dict:
    """The usage block of a Chat Completions reply: what the request was, and what the reply is, in tokens."""
    prompt = REPLY_START + sum(message_tokens(m) for m in body.get("messages") or [])
    if body.get("tools"):
        prompt += count(json.dumps(body["tools"]))
    completion = count(_text(reply_message.get("content"))) + _calls(reply_message)
    return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": prompt + completion}
