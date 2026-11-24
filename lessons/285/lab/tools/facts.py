"""Print the exact names and signatures of the installed libraries, so nothing is quoted from memory.

    python -m tools.facts
"""
import inspect
from importlib.metadata import version

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend, StoreBackend
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

for name in ("langchain", "langchain-core", "langchain-openai", "langgraph", "langgraph-checkpoint-postgres", "deepagents"):
    print(f"{name}=={version(name)}")

print("\nChatOpenAI: the parameter name to pass, then the field it fills and its default")
for field in ("model_name", "openai_api_base", "openai_api_key", "use_responses_api", "default_headers", "max_retries"):
    info = ChatOpenAI.model_fields[field]
    print(f"  {info.alias or field:<18} field {field:<18} default {info.default!r}")

print()
for label, thing in (("create_agent", create_agent), ("create_deep_agent", create_deep_agent),
                     ("StateBackend", StateBackend.__init__), ("FilesystemBackend", FilesystemBackend.__init__),
                     ("StoreBackend", StoreBackend.__init__), ("CompositeBackend", CompositeBackend.__init__),
                     ("PostgresSaver.from_conn_string", PostgresSaver.from_conn_string),
                     ("PostgresStore.from_conn_string", PostgresStore.from_conn_string)):
    params = inspect.signature(thing).parameters
    print(f"{label}(" + ", ".join(n + ("=" + repr(p.default) if p.default is not p.empty else "")
                                   for n, p in params.items() if n != "self") + ")")
