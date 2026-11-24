"""The payables agent as a service: the door in front of the agent.

    POST /runs                      {"thread_id": "friday-2026-11-27"}   start the Friday payment run under that
                                    name, or carry on with it when Postgres holds unfinished work for it
    GET  /runs/{thread_id}          where the run stands: working, waiting for a person, stopped, or finished
    POST /runs/{thread_id}/decision {"type": "approve"} | {"type": "edit", "amount_usd": 3000.0} |
                                    {"type": "reject", "message": "why"}: a person's answer to the waiting payment
    GET  /health

Every call but /health needs the header X-Service-Token. A person, a web page or a schedule can be the caller.
The service keeps nothing about a run between two calls: the run's state is in Postgres. Kill the container,
start it again, send POST /runs with the same thread_id, and the run goes on.
The agent behind it has every part on: helpers, memory, the policy, the receiving agent, and the approval pause.
"""
import os
import threading
import traceback

from fastapi import Depends, FastAPI, Header, HTTPException
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.types import Command
from pydantic import BaseModel

from app import policy_index
from app.control import begin
from app.payables_agent import Context, build_agent
from app.prompts import PAYMENT_RUN

AGENT_DB = os.environ["AGENT_DB_URL"]
TOKEN = os.environ.get("SERVICE_TOKEN", "")
TASK = PAYMENT_RUN + " Tell each checker to read /memories/AGENTS.md first."
PARTS = dict(checker=True, memory=True, policy=True, receiving=True, approvals=True)
WORKING: dict[str, threading.Thread] = {}     # which runs this process is working on right now; nothing else is kept
LAST_ERROR: dict[str, str] = {}

app = FastAPI(title="Juniper Market payables agent")


def caller(x_service_token: str = Header(default="")) -> None:
    """Who may call: only a caller that knows the service's token."""
    if not TOKEN or x_service_token != TOKEN:
        raise HTTPException(status_code=401, detail="X-Service-Token is missing or wrong")


def with_agent(use):
    """Open the agent's database, build the agent, use it, and close everything again."""
    with PostgresSaver.from_conn_string(AGENT_DB) as saver, PostgresStore.from_conn_string(AGENT_DB) as store:
        saver.setup()
        store.setup()
        policy_index.ensure()
        return use(build_agent(checkpointer=saver, store=store, **PARTS))


def config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def work(thread_id: str, send) -> None:
    """One stretch of work in the background: until the run waits for a person, ends, or fails."""
    try:
        with_agent(lambda agent: agent.invoke(send, config(thread_id), context=Context()))
    except Exception:      # kept for GET /runs/{thread_id}, not hidden
        LAST_ERROR[thread_id] = traceback.format_exc(limit=3)
    finally:
        WORKING.pop(thread_id, None)


def start_work(thread_id: str, send) -> None:
    LAST_ERROR.pop(thread_id, None)
    WORKING[thread_id] = threading.Thread(target=work, args=(thread_id, send), daemon=True)
    WORKING[thread_id].start()


def read(thread_id: str) -> dict:
    """Where the run stands, read from Postgres. While this process works on the run it says so and reads
    nothing: a state read in the middle of a step can look finished when it is not."""
    if thread_id in WORKING:
        return {"thread_id": thread_id, "status": "working"}

    def look(agent):
        state = agent.get_state(config(thread_id))
        messages = state.values.get("messages", [])
        out = {"thread_id": thread_id, "messages_saved": len(messages)}
        if thread_id in WORKING:
            return {"thread_id": thread_id, "status": "working"}
        if state.interrupts:
            asked = state.interrupts[0].value["action_requests"][0]
            return {**out, "status": "waiting_for_a_person", "waiting_for": {"tool": asked["name"], "args": asked["args"]}}
        if state.next:
            return {**out, "status": "stopped", "next": list(state.next),
                    "note": "unfinished work is saved in Postgres; POST /runs with this thread_id carries on",
                    **({"last_error": LAST_ERROR[thread_id]} if thread_id in LAST_ERROR else {})}
        if messages and not getattr(messages[-1], "tool_calls", None):
            return {**out, "status": "finished", "result": messages[-1].content}
        if thread_id in LAST_ERROR:
            return {**out, "status": "failed", "last_error": LAST_ERROR[thread_id]}
        return {**out, "status": "unknown"}
    return with_agent(look)


class Run(BaseModel):
    thread_id: str


class Decision(BaseModel):
    type: str
    amount_usd: float | None = None
    message: str | None = None


@app.get("/health")
def health():
    return {"ok": True, "agent": "payables-agent"}


@app.post("/runs", status_code=202, dependencies=[Depends(caller)])
def start(run: Run):
    now = read(run.thread_id)
    if now["status"] in ("working", "waiting_for_a_person", "finished"):
        return {**now, "started": "nothing: the run is " + now["status"].replace("_", " ")}
    begin(f"service-{run.thread_id}", None, fresh=now["status"] == "unknown")     # only names the scripted model's log
    if now["status"] == "stopped":      # unfinished work in Postgres: go on from the last saved step, with no new input
        start_work(run.thread_id, None)
        return {**now, "status": "working", "started": "carrying on from the last saved step"}
    start_work(run.thread_id, {"messages": [{"role": "user", "content": TASK}]})
    return {"thread_id": run.thread_id, "status": "working", "started": "a new run"}


@app.get("/runs/{thread_id}", dependencies=[Depends(caller)])
def status(thread_id: str):
    now = read(thread_id)
    if now["status"] == "unknown":
        raise HTTPException(status_code=404, detail=f"no run is saved under {thread_id}")
    return now


@app.post("/runs/{thread_id}/decision", status_code=202, dependencies=[Depends(caller)])
def decide(thread_id: str, decision: Decision):
    now = read(thread_id)
    if now["status"] != "waiting_for_a_person":
        raise HTTPException(status_code=409, detail=f"the run is {now['status']}, not waiting for a person")
    asked = now["waiting_for"]
    if decision.type == "approve":
        answer = {"type": "approve"}
    elif decision.type == "edit" and decision.amount_usd is not None:
        answer = {"type": "edit", "edited_action": {"name": asked["tool"], "args": {**asked["args"], "amount_usd": decision.amount_usd}}}
    elif decision.type == "reject":
        answer = {"type": "reject", "message": decision.message or "Rejected."}
    else:
        raise HTTPException(status_code=422, detail="type is approve, edit (with amount_usd) or reject")
    begin(f"service-{thread_id}", None, fresh=False)
    start_work(thread_id, Command(resume={"decisions": [answer]}))
    return {"thread_id": thread_id, "status": "working", "answered": asked, "decision": answer}
