"""The same agent from LangChain's parts: a model, two tools, and create_agent, which is the loop.

    python agent_langchain.py          ask the same question as agent_by_hand.py
    python agent_langchain.py graph    print the graph create_agent built: its nodes and its edges
    python agent_langchain.py run      the same agent with five tools and the real job: the Friday payment run,
                                       40 invoices in one conversation, nothing saved
"""
import sys

from langchain.agents import create_agent

from app.common import READ_TOOLS, WRITE_TOOLS, get_invoice, get_purchase_order, make_model
from app.control import begin
from app.prompts import PAYMENT_RUN, QUESTION, SYSTEM

agent = create_agent(model=make_model(), tools=[get_invoice, get_purchase_order], system_prompt=SYSTEM)


def show(messages) -> None:
    """Print a conversation the way agent_by_hand.py prints it."""
    for m in messages:
        if m.type == "ai" and m.tool_calls:
            for call in m.tool_calls:
                args = ", ".join(f'"{k}": {v!r}'.replace("'", '"') for k, v in call["args"].items())
                print(f"model asks   {call['name']}({{{args}}})")
        elif m.type == "tool":
            print(f"we answer    {len(m.content):,} characters: {m.content[:110]}...")
        else:
            print(f"{({'human': 'user', 'ai': 'assistant'}.get(m.type, m.type)):<12} {m.content}")
    print(f"\n{sum(1 for m in messages if m.type == 'ai')} requests to the model, "
          f"{sum(1 for m in messages if m.type == 'tool')} tool calls run by our code")


if __name__ == "__main__":
    if sys.argv[1:2] == ["graph"]:
        graph = agent.get_graph()
        print("type:", type(agent).__module__ + "." + type(agent).__name__)
        print("nodes:", list(graph.nodes))
        for edge in graph.edges:
            print(f"edge: {edge.source} -> {edge.target}" + (" (conditional)" if edge.conditional else ""))
    elif sys.argv[1:2] == ["run"]:
        begin("s3-run", int(sys.argv[2]) if len(sys.argv) > 2 else 0)
        runner = create_agent(model=make_model(), tools=[*READ_TOOLS, *WRITE_TOOLS], system_prompt=SYSTEM)
        result = runner.invoke({"messages": [{"role": "user", "content": PAYMENT_RUN}]})
        print(f"{sum(1 for m in result['messages'] if m.type == 'ai')} requests to the model, "
              f"{sum(1 for m in result['messages'] if m.type == 'tool')} tool calls run by our code, "
              f"{len(result['messages'])} messages in the conversation\n")
        print(result["messages"][-1].content)
    else:
        question = sys.argv[1] if len(sys.argv) > 1 else QUESTION
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        print(f"{'system':<12} {SYSTEM}")
        show(result["messages"])
