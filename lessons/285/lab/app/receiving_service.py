"""The receiving agent: the warehouse's own agent, as its own small service with its own database.

It is a second agent, not a helper inside the first one: its own prompt, its own tool, its own data.
The payables agent cannot read the receiving database. It can only ask this service a question.

    POST /ask {"question": "What arrived for purchase order PO-2207?"}  ->  {"answer": "..."}
"""
import json
import os

import psycopg
from fastapi import FastAPI
from langchain.agents import create_agent
from langchain.tools import tool
from psycopg.rows import dict_row
from pydantic import BaseModel

from app.common import make_model

DB_URL = os.environ["RECEIVING_DB_URL"]
SYSTEM = ("You are the receiving agent of Juniper Market's warehouse. You answer questions about what arrived "
          "at the dock. Read the receipts with your tool. Answer with one line for each product. Never guess.")


@tool
def get_receipts(po_number: str) -> str:
    """Get the receipts for a purchase order: the date, the dock, who signed, and the quantity received of each product."""
    with psycopg.connect(DB_URL, row_factory=dict_row) as db:
        receipts = db.execute("SELECT receipt_id, po_number, received_date, dock, received_by FROM receipts"
                              " WHERE po_number = %s ORDER BY receipt_id", (po_number,)).fetchall()
        for receipt in receipts:
            receipt["lines"] = db.execute(
                "SELECT line_no, sku, description, quantity_received, unit FROM receipt_lines"
                " WHERE receipt_id = %s ORDER BY line_no", (receipt["receipt_id"],)).fetchall()
    return json.dumps({"po_number": po_number, "receipts": receipts}, default=str)


agent = create_agent(model=make_model("receiving-agent"), tools=[get_receipts], system_prompt=SYSTEM)
app = FastAPI(title="Juniper Market receiving agent")


class Question(BaseModel):
    question: str


def answer(question: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].content


@app.get("/health")
def health():
    return {"ok": True, "agent": "receiving-agent"}


@app.post("/ask")
def ask(q: Question):
    return {"agent": "receiving-agent", "answer": answer(q.question)}


# ---------------------------------------------------------------- the same agent, reachable over A2A
# Agent2Agent (A2A) is an open protocol for one agent calling another: a card that says what the agent does,
# a message to send, and a task to follow. The library is a2a-sdk; nothing here needs a hosted product.
import asyncio  # noqa: E402

from a2a.helpers import new_task_from_user_message, new_text_part  # noqa: E402
from a2a.server.agent_execution import AgentExecutor, RequestContext  # noqa: E402
from a2a.server.events import EventQueue  # noqa: E402
from a2a.server.request_handlers import DefaultRequestHandler  # noqa: E402
from a2a.server.routes import add_a2a_routes_to_fastapi, create_agent_card_routes, create_jsonrpc_routes  # noqa: E402
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater  # noqa: E402
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill  # noqa: E402

A2A_SECONDS = float(os.environ.get("RECEIVING_A2A_SECONDS", "0"))    # a slow warehouse lookup, for the lab

CARD = AgentCard(
    name="Juniper Market receiving agent",
    description="Says what really arrived at the warehouse dock for a purchase order.",
    version="0.1.0",
    supported_interfaces=[AgentInterface(url=os.environ.get("RECEIVING_AGENT_URL", "http://receiving-agent:8000") + "/a2a",
                                         protocol_binding="JSONRPC", protocol_version="1.0")],
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[AgentSkill(id="what-arrived", name="What arrived for a purchase order",
                       description="Give a purchase order number. The answer has one line for each product received.",
                       tags=["receiving", "warehouse"], examples=["What arrived for purchase order PO-2207?"])],
)


class ReceivingExecutor(AgentExecutor):
    """What the A2A library calls for each incoming message: open a task, run our agent, report the answer."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task
        if task is None:
            task = new_task_from_user_message(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.start_work()
        await asyncio.sleep(A2A_SECONDS)
        text = await asyncio.to_thread(answer, context.get_user_input())
        await updater.add_artifact([new_text_part(text)], name="answer")
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()


handler = DefaultRequestHandler(agent_executor=ReceivingExecutor(), task_store=InMemoryTaskStore(), agent_card=CARD)
add_a2a_routes_to_fastapi(app, agent_card_routes=create_agent_card_routes(CARD),
                          jsonrpc_routes=create_jsonrpc_routes(handler, rpc_url="/a2a"))
