"""The payables agent as a deep agent. Every later part is one argument of build_agent().

    build_agent()                                   the loop, the file tools and the task tool
    build_agent(backend=FilesystemBackend(...))     its files on a real disk
    build_agent(checkpointer=...)                   every step saved, so it can resume and wait
    build_agent(approvals=True, checkpointer=...)   a person decides before schedule_payment runs
    build_agent(memory=True, store=...)             /memories/ kept in a store, across conversations
    build_agent(checker=True)                       a subagent that checks one invoice on a clean page
    build_agent(policy=True)                        search_policy, backed by a vector table
    build_agent(receiving=True)                     ask_receiving, a question to the warehouse's agent over HTTP
    build_agent(receiving="a2a")                    the same question over the Agent2Agent protocol
    build_agent(receiving="later")                  the question sent without waiting, and its answer read later
    build_agent(call_cap=20)                        at most 20 requests to the model on one thread of this agent
    build_agent(memory=True, protect_memory=True)   the file tools may read /memories/ and may not write there
"""
import os
from dataclasses import dataclass

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain.agents.middleware import ModelCallLimitMiddleware

from app.common import (READ_TOOLS, WRITE_TOOLS, ask_receiving, ask_receiving_a2a, get_invoice, get_purchase_order,
                        make_model, receiving_answer, send_to_receiving)
from app.prompts import MEMORY_FIRM, SYSTEM


@dataclass
class Context:
    """What our own service knows about a run and hands to the agent. Without Agent Server this is where it lives."""
    org_id: str = "juniper-market"


CHECKER = {
    "name": "invoice-checker",
    "description": "Checks one supplier invoice against its purchase order and answers with one line, PAY or HOLD. "
                   "Give it one invoice per task.",
    "system_prompt": "You check one supplier invoice for Juniper Market. Read the invoice and its purchase order with "
                     "your tools and compare every line. Reply with one line: PAY <invoice number> <amount> <short note>, "
                     "or HOLD <invoice number> <reason>. Never guess.",
    "tools": [get_invoice, get_purchase_order],
}


def memory_namespace(runtime):
    """Where this run's memory files live in the store: one namespace per organization."""
    return (runtime.context.org_id,)


def build_agent(*, tools=None, backend=None, checkpointer=None, store=None, approvals=False, memory=False,
                checker=False, policy=False, receiving=False, call_cap=None, protect_memory=False):
    tools = list(tools) if tools is not None else [*READ_TOOLS, *WRITE_TOOLS]
    extra = []
    if receiving == "later":    # two tools: send the question and get a task id, then read the answer when needed
        extra += [send_to_receiving, receiving_answer]
    elif receiving:    # True: a plain HTTP request. "a2a": the same question over the Agent2Agent protocol
        extra.append(ask_receiving_a2a if receiving == "a2a" else ask_receiving)
    if policy:
        from app.policy_index import search_policy
        extra.append(search_policy)
    tools += extra
    more, system = {}, SYSTEM
    if memory:
        backend = CompositeBackend(default=backend or StateBackend(),
                                   routes={"/memories/": StoreBackend(namespace=memory_namespace)})
        more.update(memory=["/memories/AGENTS.md"], context_schema=Context)
        if os.environ.get("MEMORY_FIRM") == "1":    # a firmer instruction of our own, for a small model
            system = SYSTEM + "\n\n" + MEMORY_FIRM
        if protect_memory:    # permissions know read and write; delete counts as a write
            more["permissions"] = [FilesystemPermission(operations=["write"], paths=["/memories/**"], mode="deny")]
    if approvals:
        more["interrupt_on"] = {"schedule_payment": True}
    if checker:      # the helper gets the lookups it needs, and never the tools that write
        more["subagents"] = [{**CHECKER, "tools": [*CHECKER["tools"], *extra]}]
    if call_cap:     # counted per thread, so a resume or an approval does not reset it. It counts this agent's own
        # requests: a helper is another agent and would need a cap of its own.
        more["middleware"] = [ModelCallLimitMiddleware(thread_limit=int(call_cap), exit_behavior="end")]
    return create_deep_agent(model=make_model(), tools=tools, system_prompt=system, backend=backend,
                             checkpointer=checkpointer, store=store, **more)
