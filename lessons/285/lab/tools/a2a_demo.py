"""Talk to the receiving agent over the A2A protocol, with the protocol's own library (a2a-sdk).

    python -m tools.a2a_demo send PO-2220    send a message and wait for the finished task
    python -m tools.a2a_demo later PO-2220   send without waiting, get a task id back, and check on it later

The agent card, what the other agent says it can do, is a plain GET:
    python -m tools.http GET http://receiving-agent:8000/.well-known/agent-card.json
"""
import asyncio
import os
import sys
import time

from a2a.client import ClientConfig, ClientFactory
from a2a.helpers import get_artifact_text, new_text_message
from a2a.types import GetTaskRequest, Role, SendMessageConfiguration, SendMessageRequest, TaskState
from google.protobuf.json_format import MessageToJson

BASE = os.environ["RECEIVING_AGENT_URL"]


def show(label: str, message) -> None:
    print(f"{label}:\n{MessageToJson(message, indent=2)}\n")


async def main(command: str, po: str = "PO-2220") -> None:
    client = await ClientFactory(ClientConfig(streaming=False)).create_from_url(BASE)
    question = new_text_message(f"What arrived for purchase order {po}?", role=Role.ROLE_USER)
    if command == "send":
        async for event in client.send_message(SendMessageRequest(message=question)):
            show("what came back", event)
            if event.HasField("task"):
                print("state:", TaskState.Name(event.task.status.state))
                for artifact in event.task.artifacts:
                    print("answer:\n" + get_artifact_text(artifact))
    elif command == "later":
        started = time.monotonic()
        request = SendMessageRequest(message=question, configuration=SendMessageConfiguration(return_immediately=True))
        task = None
        async for event in client.send_message(request):
            task = event.task
        print(f"{time.monotonic() - started:.2f} s: the send returned. task {task.id}, state {TaskState.Name(task.status.state)}, "
              f"{len(task.artifacts)} artifacts")
        print("... the caller is free to do other work here ...")
        while True:
            await asyncio.sleep(0.5)
            task = await client.get_task(GetTaskRequest(id=task.id))
            print(f"{time.monotonic() - started:.2f} s: get_task says {TaskState.Name(task.status.state)}, {len(task.artifacts)} artifacts")
            if task.status.state != TaskState.TASK_STATE_WORKING and task.status.state != TaskState.TASK_STATE_SUBMITTED:
                break
        for artifact in task.artifacts:
            print("answer:\n" + get_artifact_text(artifact))
    await client.close()


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("send", "later"):
        sys.exit(__doc__)
    asyncio.run(main(*sys.argv[1:3]))
