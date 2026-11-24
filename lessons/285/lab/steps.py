"""The deep agent, one part at a time. Each command runs one small proof and prints what it saw.

    python steps.py s4-bare      a bare deep agent answers the same question
    python steps.py s4-write     it writes a file: where does the file live?
    python steps.py s4-large     one very large tool result
    python steps.py s4-disk      the same file tools on a real folder
    python steps.py s5-setup     create LangGraph's checkpoint tables in the agent database
    python steps.py s5-one T     one invoice, saved under thread id T
    python steps.py s5-run T [ms]   the Friday payment run under thread id T; started again, it resumes
    python steps.py s5-nosave TAG [ms] [helpers]   the same run with nothing saved; started again, it starts over
    python steps.py s5-show T    the saved conversation of thread T, with every ask of the model in full
    python steps.py s6-ask T N   check invoice N and pay it, with an approval pause before schedule_payment
    python steps.py s6-decide T approve | edit AMOUNT | reject "why"     answer the pause of thread T
    python steps.py s6-no-checkpointer   the same pause with nothing to save it in
    python steps.py s7-setup     create the store's tables in the agent database
    python steps.py s7-ask T N [ORG]     check invoice N with the memory file loaded, thread id T
    python steps.py s7-remember T [ORG] ["rule"]   tell the agent a rule; it writes the rule to its memory file
    python steps.py s7-server-info   the namespace the docs show, without Agent Server
    python steps.py s8-direct T | s8-delegate T [ms] | s8-delegate-memory T [N]   the payment run, in one conversation or
                                 delegated; with N, the last one ends after N requests of our agent
    python steps.py s9-ask N     check invoice N with search_policy on offer
    python steps.py s9-pay T N   check invoice N and pay it: the pause again, with the policy saying who approves
    python steps.py s9-decide T approve | edit AMOUNT | reject "why"     answer that pause
    python steps.py s10-ask N [a2a] [nopolicy]   check invoice N, asking the receiving agent what arrived (HTTP, or A2A)
    python steps.py s10-two wait | later [A B]   two invoices that need the warehouse: wait for each answer, or send
                                                 both questions first and read the answers later
    python steps.py s10-pay T N  check invoice N and pay it, with the warehouse and the policy on offer: the pause
                                 shows the amount it asks to schedule
    python steps.py s10-run T [ms]   the payment run with every part switched on
    python steps.py s11-cap T N  the delegated payment run, stopped after N requests to the model
    python steps.py s11-delete T [protect]   ask the agent to delete its memory file; with protect, a permission refuses
    python steps.py s11-remember T [protect] ask it to remember a rule; the same permission refuses that too
"""
import json
import os
import sys
import time

from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.types import Command

from app.common import READ_TOOLS, get_invoice, get_purchase_order
from app.control import begin
from app.payables_agent import Context, build_agent
from app.prompts import PAYMENT_RUN, QUESTION

AGENT_DB = os.environ["AGENT_DB_URL"]


def ask(agent, text, **kwargs):
    return agent.invoke({"messages": [{"role": "user", "content": text}]}, **kwargs)


def show(result, full=False) -> None:
    """The conversation as it stands in the agent's state. full: every ask with its whole text, and what the model
    wrote beside an ask."""
    for m in result["messages"]:
        if m.type == "ai" and m.tool_calls:
            if full and str(m.content).strip():
                print(f"model says   {' '.join(str(m.content).split())}")
            for call in m.tool_calls:
                shown = {k: (v if full or len(str(v)) < 90 else str(v)[:90] + "...") for k, v in call["args"].items()}
                print(f"model asks   {call['name']}({shown})")
        elif m.type == "tool":
            print(f"we answer    {len(m.content):,} characters: {' '.join(m.content[:110].split())}...")
        else:
            print(f"{({'human': 'user', 'ai': 'assistant'}.get(m.type, m.type)):<12} {m.content}")
    print(f"\n{sum(1 for m in result['messages'] if m.type == 'ai')} requests to the model, "
          f"{sum(1 for m in result['messages'] if m.type == 'tool')} tool calls")


def show_files(result) -> None:
    files = result.get("files") or {}
    print(f"\nstate keys: {sorted(result)}")
    print(f"files in the state: {len(files)}")
    for path, data in files.items():
        print(f"  {path}  {len(data['content']):,} characters, encoding {data['encoding']}, created {data['created_at']}")


def s4_bare():
    begin("s4-bare")
    show(ask(build_agent(tools=[get_invoice, get_purchase_order]), QUESTION))


def s4_write():
    begin("s4-write")
    result = ask(build_agent(tools=[get_invoice, get_purchase_order]), QUESTION + " Save your finding to /findings/1042.md.")
    show(result)
    show_files(result)
    print("content of /findings/1042.md in the state:")
    print("  " + result["files"]["/findings/1042.md"]["content"])


def s4_large():
    begin("s4-large")
    result = ask(build_agent(tools=READ_TOOLS), "Load every invoice due on 2026-11-27 with its full document text.")
    show(result)
    show_files(result)
    stub = next(m for m in result["messages"] if m.type == "tool")
    print(f"\nthe tool message the model saw, all {len(stub.content):,} characters of it:\n{stub.content}")


def s4_disk():
    begin("s4-disk")
    agent = build_agent(tools=[get_invoice, get_purchase_order], backend=FilesystemBackend(root_dir="/workspace"))
    result = ask(agent, QUESTION + " Save your finding to /findings/1042.md.")
    show(result)
    print(f"\nstate keys: {sorted(result)}")


def s5_setup():
    with PostgresSaver.from_conn_string(AGENT_DB) as saver:
        saver.setup()
    print("PostgresSaver.setup() finished")


def s5_one(thread):
    begin(f"s5-{thread}")
    with PostgresSaver.from_conn_string(AGENT_DB) as saver:
        agent = build_agent(tools=[get_invoice, get_purchase_order], checkpointer=saver)
        config = {"configurable": {"thread_id": thread}}
        show(ask(agent, QUESTION, config=config))
        state = agent.get_state(config)
        print(f"\nsaved state of thread {thread}: {len(state.values['messages'])} messages, next node {state.next}, "
              f"checkpoint {state.config['configurable']['checkpoint_id']}")


def payment_run(thread, tag, delay_ms=0, text=PAYMENT_RUN, approve_all=False, **parts):
    """The Friday payment run. A thread that has unfinished work in Postgres is resumed, not started again."""
    with PostgresSaver.from_conn_string(AGENT_DB) as saver, PostgresStore.from_conn_string(AGENT_DB) as store:
        saver.setup()
        agent = build_agent(checkpointer=saver, store=store if parts.get("memory") else None, **parts)
        config = {"configurable": {"thread_id": thread}}
        more = {"context": Context()} if parts.get("memory") else {}
        state = agent.get_state(config)
        saved = state.values.get("messages", [])
        if state.next:
            begin(tag, delay_ms, fresh=False)
            last = saved[-1]
            what = f"asks {last.tool_calls[0]['name']}({last.tool_calls[0]['args']})" if getattr(last, "tool_calls", None) \
                else " ".join(str(last.content)[:120].split())
            print(f"thread {thread}: unfinished work found in Postgres: {len(saved)} messages saved, next node {state.next}")
            print(f"last saved message: {last.type} {what}")
            print("resuming with invoke(None, config): no new input", flush=True)
            result = agent.invoke(None, config, **more)
        elif saved:
            print(f"thread {thread}: already finished, {len(saved)} messages saved")
            result = state.values
        else:
            begin(tag, delay_ms)
            print(f"thread {thread}: nothing saved yet, starting the run", flush=True)
            result = ask(agent, text, config=config, **more)
        pauses = 0
        while approve_all and result.get("__interrupt__"):      # stands in for Dana clicking approve each time
            pauses += 1
            result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config, **more)
        if pauses:
            print(f"{pauses} pauses for approval, each answered with approve")
        print(f"{len(result['messages'])} messages in the conversation\n")
        print(result["messages"][-1].content)


def s5_run(thread, delay_ms="0"):
    payment_run(thread, f"s5-{thread}", int(delay_ms))


def s5_show(thread):
    """What a thread's saved steps hold of our agent's own conversation. A helper's conversation is not in it."""
    with PostgresSaver.from_conn_string(AGENT_DB) as saver:
        state = build_agent(checkpointer=saver, checker=True).get_state({"configurable": {"thread_id": thread}})
        print(f"thread {thread}: {len(state.values.get('messages', []))} messages saved, next node {state.next}")
        show(state.values, full=True)


def s5_nosave(tag, delay_ms="0", helpers=""):
    """The payment run with nothing saved. The conversation lives in this process only: killed, it is gone."""
    begin(f"s5-nosave-{tag}", int(delay_ms))
    agent = build_agent(checker=bool(helpers))
    print("no checkpointer: nothing of this run is saved outside this process", flush=True)
    result = ask(agent, PAYMENT_RUN)
    print(f"{len(result['messages'])} messages in the conversation\n")
    print(result["messages"][-1].content)


def s8_direct(thread):
    """The whole run in one conversation: every invoice's paper stays in it."""
    payment_run(thread, f"s8-{thread}")


def s8_delegate(thread, delay_ms="0"):
    """The same run, each invoice handed to the invoice-checker subagent."""
    payment_run(thread, f"s8-{thread}", int(delay_ms), checker=True)


def s8_delegate_memory(thread, cap=""):
    """Delegated, with the memory file: each checker is told to read it, through the store, on its own.
    With a cap, the run ends after that many requests of our agent: enough to see what a slow model hands over."""
    payment_run(thread, f"s8-{thread}", checker=True, memory=True, call_cap=int(cap) if cap else None,
                text=PAYMENT_RUN + " Tell each checker to read /memories/AGENTS.md first.")


def pay_question(invoice) -> str:
    return f"Check invoice {invoice} against its purchase order and schedule its payment if it matches."


def show_pause(agent, config, result) -> None:
    print(f"\nkeys of the result: {sorted(result)}")
    for waiting in result.get("__interrupt__", []):
        print(f"interrupt {waiting.id}:")
        print(json.dumps(waiting.value, indent=2, default=str))
    state = agent.get_state(config)
    print(f"saved state: next node {state.next}, interrupts waiting {len(state.interrupts)}")


def s6_ask(thread, invoice="1031", policy=False, step="s6", receiving=False):
    begin(f"{step}-{thread}")
    with PostgresSaver.from_conn_string(AGENT_DB) as saver:
        saver.setup()
        agent = build_agent(checkpointer=saver, approvals=True, policy=policy, receiving=receiving)
        config = {"configurable": {"thread_id": thread}}
        result = ask(agent, pay_question(invoice), config=config)
        show(result)
        show_pause(agent, config, result)


def s6_decide(thread, kind, value=None, policy=False, step="s6"):
    begin(f"{step}-{thread}", fresh=False)
    with PostgresSaver.from_conn_string(AGENT_DB) as saver:
        agent = build_agent(checkpointer=saver, approvals=True, policy=policy)
        config = {"configurable": {"thread_id": thread}}
        asked = agent.get_state(config).interrupts[0].value["action_requests"][0]
        decision = {"approve": lambda: {"type": "approve"},
                    "edit": lambda: {"type": "edit", "edited_action": {
                        "name": asked["name"], "args": {**asked["args"], "amount_usd": float(value)}}},
                    "reject": lambda: {"type": "reject", "message": value or "Rejected."}}[kind]()
        print(f"the waiting tool call: {asked['name']}({asked['args']})")
        print(f"the decision we send: Command(resume={{'decisions': [{decision}]}})\n")
        result = agent.invoke(Command(resume={"decisions": [decision]}), config)
        show(result)
        show_pause(agent, config, result)


def s6_no_checkpointer(invoice="1036"):
    begin("s6-no-checkpointer")
    agent = build_agent(approvals=True)
    try:
        result = ask(agent, pay_question(invoice))
        show(result)
        print(f"\nkeys of the result: {sorted(result)}")
        print("now the answer: agent.invoke(Command(resume=...)) with no thread to find", flush=True)
        result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}))
        show(result)
    except Exception as error:      # shown as evidence, not hidden
        print(f"\n{type(error).__name__}: {error}")


RULE = "Cascade Packaging bills freight on its own line; this is agreed; pay it when it is $75 or less."


def s7_setup():
    with PostgresStore.from_conn_string(AGENT_DB) as store:
        store.setup()
    print("PostgresStore.setup() finished")


def s7_ask(thread, invoice="1034", org="juniper-market", text=None):
    with PostgresSaver.from_conn_string(AGENT_DB) as saver, PostgresStore.from_conn_string(AGENT_DB) as store:
        agent = build_agent(tools=[get_invoice, get_purchase_order], checkpointer=saver, store=store, memory=True)
        config = {"configurable": {"thread_id": thread}}
        begin(f"s7-{thread}", fresh=not agent.get_state(config).values)
        text = text or f"Is invoice {invoice} correct? Check it against its purchase order."
        print(f"thread {thread}, context org_id={org}")
        show(ask(agent, text, config=config, context=Context(org_id=org)))


def s7_remember(thread, org="juniper-market", rule=RULE):
    s7_ask(thread, org=org, text=f"Remember this for next time: {rule}")


def s7_server_info():
    """The docs' namespace reads rt.server_info, which only Agent Server fills in."""
    from deepagents import create_deep_agent
    from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

    from app.common import make_model

    def namespace_from_the_docs(rt):
        print(f"in the namespace function: rt.context={rt.context!r}")
        print(f"in the namespace function: rt.server_info={rt.server_info!r}")
        print(f"in the namespace function: rt.execution_info={rt.execution_info!r}", flush=True)
        return (rt.server_info.user.identity,)

    begin("s7-server-info")
    with PostgresStore.from_conn_string(AGENT_DB) as store:
        agent = create_deep_agent(
            model=make_model(), memory=["/memories/AGENTS.md"], store=store, context_schema=Context,
            backend=CompositeBackend(default=StateBackend(),
                                     routes={"/memories/": StoreBackend(namespace=namespace_from_the_docs)}))
        try:
            show(ask(agent, f"Remember this for next time: {RULE}", context=Context()))
        except Exception as error:      # shown as evidence, not hidden
            print(f"\n{type(error).__name__}: {error}")


def s9_ask(invoice="1063"):
    begin(f"s9-invoice-{invoice}")
    agent = build_agent(tools=[get_invoice, get_purchase_order], policy=True)
    show(ask(agent, f"Is invoice {invoice} correct? Check it against its purchase order."))


def s9_pay(thread, invoice="1039"):
    """Step 6's pause again with the policy on offer: before the payment, the agent looks up who approves it."""
    s6_ask(thread, invoice, policy=True, step="s9")


def s9_decide(thread, kind, value=None):
    s6_decide(thread, kind, value, policy=True, step="s9")


def s10_ask(invoice="1055", how="http", policy="policy"):
    begin(f"s10-invoice-{invoice}" + ("-a2a" if how == "a2a" else "") + ("" if policy == "policy" else "-nopolicy"))
    agent = build_agent(tools=[get_invoice, get_purchase_order], receiving="a2a" if how == "a2a" else True,
                        policy=policy == "policy")
    show(ask(agent, f"Is invoice {invoice} correct? Check it against its purchase order."))


def s10_pay(thread, invoice="1055"):
    """Step 6's pause once more, with the warehouse's agent and the policy on offer: what amount does it ask to schedule?"""
    s6_ask(thread, invoice, policy=True, step="s10p", receiving=True)


def s10_two(how="wait", first="1055", second="1056"):
    """Two invoices that both need the warehouse, over A2A. wait: the tool waits for each answer.
    later: both questions are sent first, and the answers are read when the agent needs them."""
    begin(f"s10-two-{how}")
    agent = build_agent(tools=[get_invoice, get_purchase_order], receiving="later" if how == "later" else "a2a", policy=True)
    started = time.monotonic()
    result = ask(agent, f"Check invoices {first} and {second} against their purchase orders and against what arrived.")
    took = time.monotonic() - started
    show(result)
    print(f"the whole conversation took {took:.2f} seconds")


def s10_run(thread, delay_ms="0"):
    """Every part at once: saved steps, memory, the subagent, the policy, the second agent, and approvals."""
    payment_run(thread, f"s10-{thread}", int(delay_ms), checker=True, memory=True, policy=True, receiving=True,
                approvals=True, approve_all=True,
                text=PAYMENT_RUN + " Tell each checker to read /memories/AGENTS.md first.")


def s11_cap(thread, cap="20"):
    """A cap on calls: this agent may send the model at most N requests in one run, then the run ends."""
    payment_run(thread, f"s11-{thread}", checker=True, call_cap=int(cap))


def memory_ask(thread, text, protect):
    with PostgresSaver.from_conn_string(AGENT_DB) as saver, PostgresStore.from_conn_string(AGENT_DB) as store:
        saver.setup()
        agent = build_agent(tools=[get_invoice, get_purchase_order], checkpointer=saver, store=store, memory=True,
                            protect_memory=bool(protect))
        begin(f"s11-{thread}")
        print("permissions: " + ("write is denied under /memories/" if protect else "none"))
        show(ask(agent, text, config={"configurable": {"thread_id": thread}}, context=Context()))


def s11_delete(thread, protect=""):
    """One of the built-in file tools deletes. Asked to, the agent deletes its own memory file, unless a permission refuses."""
    memory_ask(thread, "Delete the file /memories/AGENTS.md.", protect)


def s11_remember(thread, protect=""):
    """The same permission, seen from the other side: delete counts as a write, so the rule that refuses a delete
    refuses a new memory too."""
    memory_ask(thread, "Remember this for next time: Blue Heron Dairy invoices are due in 15 days.", protect)


if __name__ == "__main__":
    command = sys.argv[1].replace("-", "_") if len(sys.argv) > 1 else ""
    if command not in globals() or not command.startswith("s"):
        sys.exit(__doc__)
    globals()[command](*sys.argv[2:])
