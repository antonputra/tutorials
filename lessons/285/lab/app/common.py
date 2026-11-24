"""What the LangChain and Deep Agents steps share: the model and the tools."""
import json
import os
import urllib.request

from langchain.tools import tool
from langchain_openai import ChatOpenAI

from app import payables

if os.environ.get("LANGSMITH_TRACING", "").lower() == "true":
    # A step is a short program, and traces are sent from a background thread. Wait for them before the program ends,
    # or the end of a run can be missing from its trace.
    import atexit

    from langchain_core.tracers.langchain import wait_for_all_tracers
    atexit.register(wait_for_all_tracers)


def make_model(agent: str = "payables-agent") -> ChatOpenAI:
    """A chat model on any OpenAI-compatible endpoint. A real run changes the three variables, not the code."""
    # The extra header only names the caller in the scripted model's log. It is not sent to a real model.
    extra = {"default_headers": {"X-Lab-Agent": agent}} if os.environ.get("FAKE_MODEL_CONTROL") else {}
    model_class = ChatOpenAI
    if os.environ.get("LANGSMITH_TRACING", "").lower() == "true":
        extra["metadata"] = {"lab_agent": agent}     # only read in a trace: which of the lab's agents made the call
        if os.environ.get("PRICE_TRACES") == "1":
            # The model is free. Price its tokens at the lab's price list, so each call in a trace shows dollars.
            from app.pricing import LABEL, PricedChatOpenAI
            model_class = PricedChatOpenAI
            extra.update(name="ChatOpenAI", metadata={"lab_agent": agent, "priced_as": LABEL})
    return model_class(model=os.environ["MODEL_NAME"], base_url=os.environ["MODEL_BASE_URL"],
                       api_key=os.environ["MODEL_API_KEY"], use_responses_api=False, **extra)


# The same plain functions the hand-written agent calls. tool() reads each name, type hints and docstring
# and builds the JSON description the model is shown.
list_invoices_due = tool(payables.list_invoices_due)
get_invoice = tool(payables.get_invoice)
get_purchase_order = tool(payables.get_purchase_order)
hold_invoice = tool(payables.hold_invoice)
schedule_payment = tool(payables.schedule_payment)
READ_TOOLS = [list_invoices_due, get_invoice, get_purchase_order]
WRITE_TOOLS = [hold_invoice, schedule_payment]


@tool
def ask_receiving(po_number: str) -> str:
    """Ask the warehouse's receiving agent what really arrived for a purchase order. It answers in plain text."""
    request = urllib.request.Request(
        os.environ["RECEIVING_AGENT_URL"] + "/ask",
        data=json.dumps({"question": f"What arrived for purchase order {po_number}?"}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)["answer"]


@tool("ask_receiving")
def ask_receiving_a2a(po_number: str) -> str:
    """Ask the warehouse's receiving agent what really arrived for a purchase order. It answers in plain text."""
    # The same question as ask_receiving, sent with the Agent2Agent protocol's own library instead of a plain POST.
    import asyncio

    from a2a.client import ClientConfig, ClientFactory
    from a2a.helpers import get_artifact_text, new_text_message
    from a2a.types import Role, SendMessageRequest

    async def call() -> str:
        client = await ClientFactory(ClientConfig(streaming=False)).create_from_url(os.environ["RECEIVING_AGENT_URL"])
        try:
            message = new_text_message(f"What arrived for purchase order {po_number}?", role=Role.ROLE_USER)
            task = None
            async for event in client.send_message(SendMessageRequest(message=message)):
                task = event.task
            return "\n".join(get_artifact_text(artifact) for artifact in task.artifacts)
        finally:
            await client.close()

    return asyncio.run(call())


# The same question again, in two halves, so the agent does not have to wait: send it and get a task id at once,
# then read the answer when the agent needs it. Between the two, the loop is free for other work.
@tool
def send_to_receiving(po_number: str) -> str:
    """Send the warehouse's receiving agent the question "what arrived for this purchase order?" and do not wait.
    Returns a task id at once. Read the answer later with receiving_answer."""
    import asyncio

    from a2a.client import ClientConfig, ClientFactory
    from a2a.helpers import new_text_message
    from a2a.types import Role, SendMessageConfiguration, SendMessageRequest, TaskState

    async def call() -> str:
        client = await ClientFactory(ClientConfig(streaming=False)).create_from_url(os.environ["RECEIVING_AGENT_URL"])
        try:
            message = new_text_message(f"What arrived for purchase order {po_number}?", role=Role.ROLE_USER)
            request = SendMessageRequest(message=message, configuration=SendMessageConfiguration(return_immediately=True))
            task = None
            async for event in client.send_message(request):
                task = event.task
            return json.dumps({"po_number": po_number, "task_id": task.id, "state": TaskState.Name(task.status.state)})
        finally:
            await client.close()

    return asyncio.run(call())


@tool
def receiving_answer(task_id: str) -> str:
    """Read the receiving agent's answer to a question sent with send_to_receiving. If the warehouse is still
    working, this waits for it, 30 seconds at most."""
    import asyncio
    import time

    from a2a.client import ClientConfig, ClientFactory
    from a2a.helpers import get_artifact_text
    from a2a.types import GetTaskRequest, TaskState

    async def call() -> str:
        client = await ClientFactory(ClientConfig(streaming=False)).create_from_url(os.environ["RECEIVING_AGENT_URL"])
        try:
            started, seen = time.monotonic(), []
            while True:
                task = await client.get_task(GetTaskRequest(id=task_id))
                state = TaskState.Name(task.status.state)
                if not seen or seen[-1] != state:
                    seen.append(state)
                if state not in ("TASK_STATE_SUBMITTED", "TASK_STATE_WORKING") or time.monotonic() - started > 30:
                    break
                await asyncio.sleep(0.2)
            return json.dumps({"task_id": task_id, "states_seen": seen, "waited_seconds": round(time.monotonic() - started, 2),
                               "answer": "\n".join(get_artifact_text(artifact) for artifact in task.artifacts)})
        finally:
            await client.close()

    return asyncio.run(call())
