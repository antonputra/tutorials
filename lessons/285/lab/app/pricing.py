"""Dollars for tokens, at a public price list.

The lab's models are free: the scripted one is not a model, and a local one runs on your own machine. A dollar
figure from this file says what the same tokens would cost at the hosted model that price-list.json names, at
its list price on the day the list was read. It is never a bill, and no cached-input discount is applied.
"""
import json
from decimal import Decimal
from pathlib import Path

from langchain_openai import ChatOpenAI

PRICES = json.loads((Path(__file__).resolve().parent.parent / "price-list.json").read_text())
PER_INPUT_TOKEN = Decimal(PRICES["usd_per_million_input_tokens"]) / 1_000_000
PER_OUTPUT_TOKEN = Decimal(PRICES["usd_per_million_output_tokens"]) / 1_000_000
PER_CACHED_INPUT_TOKEN = Decimal(PRICES["usd_per_million_cached_input_tokens"]) / 1_000_000   # never applied to a call
LABEL = (f"{PRICES['model']} list price ({PRICES['provider']}, read {PRICES['read']}): "
         f"${PRICES['usd_per_million_input_tokens']} in, ${PRICES['usd_per_million_output_tokens']} out per 1M tokens. "
         "The model that answered is free.")


def cost(input_tokens: int, output_tokens: int) -> tuple[Decimal, Decimal]:
    """What these tokens cost at the price list: the input's dollars and the output's dollars."""
    return input_tokens * PER_INPUT_TOKEN, output_tokens * PER_OUTPUT_TOKEN


def usd(amount) -> str:
    """Dollars, exact to a billionth and with at least six decimals: one call is a small fraction of a cent."""
    text = f"{Decimal(str(amount)):,.9f}"
    while text.endswith("0") and len(text.split(".")[1]) > 6:
        text = text[:-1]
    return "$" + text


class PricedChatOpenAI(ChatOpenAI):
    """The same model. Each reply's tokens are also priced at the price list, and the dollars are added to the
    reply's usage data, which is where a LangSmith trace reads a cost from. Used only with PRICE_TRACES=1."""

    def _generate(self, *args, **kwargs):
        return _priced(super()._generate(*args, **kwargs))

    async def _agenerate(self, *args, **kwargs):
        return _priced(await super()._agenerate(*args, **kwargs))


def _priced(result):
    for generation in result.generations:
        used = getattr(generation.message, "usage_metadata", None)
        if used:
            spent_in, spent_out = cost(used.get("input_tokens", 0), used.get("output_tokens", 0))
            used.update(input_cost=float(spent_in), output_cost=float(spent_out), total_cost=float(spent_in + spent_out))
    return result
