"""The policy in a vector table, and the tool that searches it.

    python -m app.policy_index build              create the table and load the 26 sections
    python -m app.policy_index search "question"  the three closest sections, with their distances
    python -m app.policy_index compare "question" ...   the three closest sections by the stand-in and by the
                                                  embedding model that is set, side by side: words against meaning
    python -m app.policy_index urls               what each library says to the other library's form of the URL

By default the embedding is a STAND-IN, not a model: HashingEmbeddings counts words in 256 buckets. Texts that
share words land close together; it knows nothing about meaning, and it needs nothing downloaded.

A real embedding model is two settings, EMBEDDING_BASE_URL and EMBEDDING_MODEL: a free one served by Ollama on
your own machine, for example http://host.docker.internal:11434 and nomic-embed-text. Nothing else changes: the
table, the search and the tool stay the same, and only the length of a vector follows the model. The table says
which embedding built it; build it again after changing the setting.
"""
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

import psycopg
from langchain.tools import tool
from psycopg import sql
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_postgres import Column, PGEngine, PGVectorStore

POLICY = Path(__file__).parent.parent / "policy" / "accounts-payable-policy.md"
TABLE = "policy_sections"
SIZE = 256
PLAIN_URL = os.environ["AGENT_DB_URL"]                                             # postgresql://...  (LangGraph, psycopg)
VECTOR_URL = PLAIN_URL.replace("postgresql://", "postgresql+psycopg://", 1)        # the form SQLAlchemy needs
SMALL_WORDS = set("a an and are as at be by for from in is it of on or that the this to we when with not no".split())


class HashingEmbeddings(Embeddings):
    """A stand-in for an embedding model: a bag of words, hashed into SIZE buckets, scaled to length 1."""

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * SIZE
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            if word in SMALL_WORDS:
                continue
            word = word[:-1] if len(word) > 3 and word.endswith("s") else word        # orders -> order
            vector[int.from_bytes(hashlib.sha256(word.encode()).digest()[:4], "big") % SIZE] += 1.0
        length = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / length for v in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(t) for t in texts]


# Some embedding models want a short instruction in front of every text, saying what the text is for. The makers of
# nomic-embed-text ask for these two: one for a text that is stored, one for a question. Only the text that is embedded
# gets the prefix; what the table keeps, and what the model is shown, is the section as it is written.
TASK_PREFIXES = {"nomic-embed-text": ("search_document: ", "search_query: ")}


class OllamaTaskEmbeddings(Embeddings):
    """An embedding model served by Ollama, with the model's own prefixes put in front of each text."""

    def __init__(self, model: str, base_url: str, document_prefix: str, query_prefix: str):
        from langchain_ollama import OllamaEmbeddings      # only needed when a real embedding model is set
        self.model = OllamaEmbeddings(model=model, base_url=base_url)
        self.document_prefix, self.query_prefix = document_prefix, query_prefix

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.embed_documents([self.document_prefix + t for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return self.model.embed_documents([self.query_prefix + text])[0]


STAND_IN = f"a stand-in that matches words, not a model: it counts words in {SIZE} buckets"


def embedding() -> tuple[Embeddings, str]:
    """The embedding in use, and one line that says what it is. That line is also written on the table it builds."""
    model, url = os.environ.get("EMBEDDING_MODEL"), os.environ.get("EMBEDDING_BASE_URL")
    if not (model and url):
        return HashingEmbeddings(), STAND_IN
    document, query = TASK_PREFIXES.get(model.split(":")[0], ("", ""))
    document = os.environ.get("EMBEDDING_DOCUMENT_PREFIX", document)      # only to try a model without its prefixes
    query = os.environ.get("EMBEDDING_QUERY_PREFIX", query)
    said = f'with "{document}" in front of a stored text and "{query}" in front of a question' if document or query \
        else "with no prefix in front of a text"
    return OllamaTaskEmbeddings(model, url, document, query), f"the embedding model {model} on Ollama, {said}"


def table_embedding() -> str | None:
    """Which embedding built the policy table, read from the table's own comment. None: there is no table."""
    with psycopg.connect(PLAIN_URL) as db:
        if db.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",)).fetchone()[0] is None:
            return None
        return db.execute("SELECT obj_description(%s::regclass, 'pg_class')", (f"public.{TABLE}",)).fetchone()[0] or STAND_IN


def sections() -> list[Document]:
    """One document for each numbered section of the policy."""
    parts = re.split(r"^## (\d+)\. (.+)$", POLICY.read_text(), flags=re.M)[1:]
    return [Document(page_content=f"{title}\n{body.strip()}", metadata={"section": int(number), "title": title})
            for number, title, body in zip(parts[0::3], parts[1::3], parts[2::3])]


_store = None


def store() -> PGVectorStore:
    global _store
    if _store is None:
        embedder, what = embedding()
        built_by = table_embedding()
        if built_by is not None and built_by != what:      # two embeddings' numbers cannot be compared
            raise RuntimeError(f"the policy table was built by {built_by}, and the embedding set now is {what}: "
                               "run python -m app.policy_index build")
        engine = PGEngine.from_connection_string(url=VECTOR_URL)
        _store = PGVectorStore.create_sync(engine=engine, table_name=TABLE, embedding_service=embedder,
                                           metadata_columns=["section", "title"])
    return _store


def build() -> None:
    global _store
    embedder, what = embedding()
    size = len(embedder.embed_query("how long is a list of numbers"))      # the length of a vector follows the model
    engine = PGEngine.from_connection_string(url=VECTOR_URL)
    engine.init_vectorstore_table(table_name=TABLE, vector_size=size, overwrite_existing=True,
                                  metadata_columns=[Column("section", "INTEGER"), Column("title", "TEXT")])
    with psycopg.connect(PLAIN_URL) as db:      # the table says which embedding built it
        db.execute(sql.SQL("COMMENT ON TABLE {} IS {}").format(sql.Identifier(TABLE), sql.Literal(what)))
    _store = None
    docs = sections()
    store().add_documents(docs)
    print(f"table {TABLE}: {len(docs)} sections loaded, {size} numbers a vector, "
          f"{sum(len(d.page_content.split()) for d in docs)} words")
    print(f"embedding: {what}")


def ensure() -> None:
    """Build the table when it does not exist yet, or was built by another embedding than the one set now, so a
    service can start on an empty agent database."""
    if table_embedding() != embedding()[1]:
        global _store
        _store = None       # the database was rebuilt under us: an engine kept from before would hold dead connections
        build()


@tool
def search_policy(question: str) -> str:
    """Search Juniper Market's accounts payable policy. Returns the three sections closest to the question."""
    hits = store().similarity_search_with_score(question, k=3)
    return json.dumps({"question": question, "results": [
        {"section": doc.metadata["section"], "title": doc.metadata["title"], "distance": round(float(distance), 4),
         "text": doc.page_content} for doc, distance in hits]})


def urls() -> None:
    from langgraph.checkpoint.postgres import PostgresSaver
    print(f"the same database, two forms of its address:\n  {PLAIN_URL}\n  {VECTOR_URL}\n")
    def round_trip(url: str) -> str:
        """Create a table, store one sentence, and find it again."""
        engine = PGEngine.from_connection_string(url=url)
        engine.init_vectorstore_table(table_name="url_test", vector_size=SIZE, overwrite_existing=True)
        test = PGVectorStore.create_sync(engine=engine, table_name="url_test", embedding_service=HashingEmbeddings())
        test.add_documents([Document(page_content="Freight is paid when it is agreed.")])
        return "stored and found: " + test.similarity_search("freight", k=1)[0].page_content

    def saver(url: str) -> str:
        with PostgresSaver.from_conn_string(url) as checkpointer:
            checkpointer.setup()
        return "connected, setup() ran"

    for label, attempt in (
        ("langchain-postgres PGEngine, postgresql+psycopg://", lambda: round_trip(VECTOR_URL)),
        ("langchain-postgres PGEngine, postgresql://", lambda: round_trip(PLAIN_URL)),
        ("LangGraph PostgresSaver, postgresql://", lambda: saver(PLAIN_URL)),
        ("LangGraph PostgresSaver, postgresql+psycopg://", lambda: saver(VECTOR_URL)),
    ):
        try:
            print(f"{label}:\n  {attempt()}")
        except Exception as error:      # shown as evidence, not hidden
            print(f"{label}:\n  {type(error).__name__}: {' '.join(str(error).split())[:300]}")


def nearest(embedder: Embeddings, question: str, docs: list[Document], vectors: list[list[float]], k: int = 3):
    """The k sections closest to the question, by cosine distance: the measure the table's search uses."""
    q = embedder.embed_query(question)

    def distance(v: list[float]) -> float:
        dot = sum(a * b for a, b in zip(q, v))
        return 1 - dot / ((math.sqrt(sum(a * a for a in q)) * math.sqrt(sum(b * b for b in v))) or 1.0)

    return sorted((distance(v), d.metadata["section"], d.metadata["title"]) for d, v in zip(docs, vectors))[:k]


def compare(questions: list[str]) -> None:
    """Words against meaning: the same questions ranked by the stand-in and by the embedding model that is set.
    It works in memory and does not touch the table."""
    embedder, what = embedding()
    if what == STAND_IN:
        sys.exit("set EMBEDDING_BASE_URL and EMBEDDING_MODEL first: there is no embedding model to compare with")
    docs, words = sections(), HashingEmbeddings()
    by_words, by_meaning = words.embed_documents([d.page_content for d in docs]), embedder.embed_documents([d.page_content for d in docs])
    print(f"left:  {STAND_IN}\nright: {what}")
    for question in questions:
        print(f"\nquestion: {question}")
        for (d1, s1, t1), (d2, s2, t2) in zip(nearest(words, question, docs, by_words), nearest(embedder, question, docs, by_meaning)):
            print(f"  {d1:.4f}  section {s1:>2}  {t1:<34} |  {d2:.4f}  section {s2:>2}  {t2}")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "build":
        build()
    elif command == "urls":
        urls()
    elif command == "search":
        print(f"embedding: {embedding()[1]}")
        try:
            hits = json.loads(search_policy.invoke({"question": sys.argv[2]}))["results"]
        except RuntimeError as error:      # the table was built by another embedding: say so in one line
            sys.exit(str(error))
        for hit in hits:
            print(f"distance {hit['distance']:.4f}  section {hit['section']:>2}  {hit['title']}")
    elif command == "compare":
        compare(sys.argv[2:])
    else:
        sys.exit(__doc__)
