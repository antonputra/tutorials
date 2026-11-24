# AI agents: the full lab

The full lab for my video "How AI Agents Actually Work: Build One From Scratch": fourteen missions, about 75 minutes, on your own computer. You build the payment agent of Juniper Market, a small grocery store in Bend, Oregon, one part at a time, from one call to a model to two agents and a service in front, and open what it really sends. The missions are on the lab's page, https://antonputra.com/labs/ai-agents/; this folder is everything they use. Short on time? The 15-minute exercise is one folder up, in [../README.md](../README.md), with its page at https://antonputra.com/exercises/ai-agents/.

Everything in it is fictional. The payables agent gets one job: the Friday payment run for November 27, 2026. Forty supplier invoices have to be checked against what was ordered and what arrived. The warehouse has its own receiving agent. A person, Dana, approves payments.

The model is a scripted stand-in (`fake_model/`): a few rules, not a model. It gets what a model gets, the messages and the tools on offer, and works out the next step from them. That's enough to show the wiring: what the agent sends, what gets saved, what happens after a crash. It shows nothing about how a real model behaves. A real model is three settings away: see [Use a real model](#use-a-real-model).

## Run it

You need Git and Docker with Compose. Nothing else: no Python on your computer, no account and no key.

```bash
docker compose up -d --build --wait
```

The first start builds the lab's image, so give it a few minutes. Later starts take seconds. No port is published, and every command runs inside a container: `docker compose exec -T lab` in front of a command runs it in the `lab` container.

| Service | What it is |
|---|---|
| `postgres` | PostgreSQL 18 with pgvector. Three databases: `juniper` (the store's business data), `receiving` (the warehouse's data) and `agent` (the agent's own: saved steps, memory, the policy's vectors). |
| `seed` | Runs once. Creates the databases and loads the same data every time. |
| `fake-model` | The scripted model. It speaks the OpenAI-compatible Chat Completions API, writes every request it gets to a file, and returns counted tokens with every reply. |
| `receiving-agent` | The second agent, as its own service: `POST /ask`, and the same agent over the A2A protocol. |
| `payables-agent` | Our agent as a service, with every part on: `POST /runs`, `GET /runs/<name>`, `POST /runs/<name>/decision`. Its callers send a token. |
| `lab` | Where you run the missions. |

`tools/all-steps.sh` runs every step of the lab in order, with a line for each: ok or FAILED. It rebuilds the data first, so it can be repeated, and takes about six minutes. It leaves out the kill of the service.

## Read what the agent sent

The scripted model writes each request to its own file, exactly as the agent sent it: the tools, the system prompt, the memory file's text and a helper's separate conversation.

```bash
docker compose exec -T lab python -m tools.reqlog tags                 # one folder for each run
docker compose exec -T lab python -m tools.reqlog ls s4-bare           # one line a request: size, messages, tools, the reply
docker compose exec -T lab python -m tools.reqlog tools s4-bare 1      # the tools on offer in request 1
docker compose exec -T lab python -m tools.reqlog system s4-bare 1     # its system prompt
docker compose exec -T lab python -m tools.reqlog messages s4-bare 3   # every message of request 3
docker compose exec -T lab python -m tools.reqlog split s8-delegate-1  # the requests grouped by who sent them
```

## Tokens and dollars

The scripted model has no tokenizer of its own. It counts with an open-source one, `tiktoken` with the encoding `o200k_base` (`fake_model/tokens.py`), and returns the counts with every reply. A hosted model counts with its own tokenizer, so its numbers for the same request are near these, not equal to them.

Both of the lab's models are free. A dollar figure says what the same tokens would cost at one named hosted model, at its public list price on the day the list was read: `price-list.json`, OpenAI's `gpt-6-luna`, $0.10 for 1M input tokens and $0.50 for 1M output tokens, read on November 21, 2026. No cached-input discount is applied. It's never a bill.

```bash
docker compose exec -T lab python -m tools.price 59 350           # one call: tokens in, tokens out
docker compose exec -T lab python -m tools.price hand             # the hand-written loop, with tokens and dollars for each request
docker compose exec -T lab python -m tools.price log s3-run       # every request of one run, from its log, and the sum by sender
```

## Start over

```bash
docker compose exec -T lab python -m seed.seed --reset-activity    # empty payments, holds and the access log
docker compose exec -T lab python -m seed.seed --reset             # rebuild the business data: same seed, same data
docker compose exec -T lab python -m seed.seed --reset-agent       # empty the agent's database: saved steps, memory, vectors
```

A conversation is kept under its thread ID (`friday-k`, `dana-approve`, `delegate-1`). A payment run whose thread already finished is not run again: the step prints "already finished". Use a new ID, or empty the agent's database. After `--reset-agent`, run `python steps.py s5-setup`, `python steps.py s7-setup` and `python -m app.policy_index build` again.

## Use a real model

The agents take three values from the environment: `MODEL_BASE_URL`, `MODEL_NAME` and `MODEL_API_KEY`. Any endpoint that speaks the OpenAI-compatible Chat Completions API fits, a free local model on Ollama too. Set `FAKE_MODEL_CONTROL` to empty, so nothing tries to steer the scripted model. Keep a key in a file outside this repository:

```bash
# ~/.config/juniper-lab/model.env
MODEL_BASE_URL=<the endpoint, ending in /v1>
MODEL_NAME=<the model's name>
MODEL_API_KEY=<the key>
FAKE_MODEL_CONTROL=
```

```bash
docker compose --env-file ~/.config/juniper-lab/model.env up -d --build --wait
```

For a free local model on Ollama on the same computer, the address is `http://host.docker.internal:11434/v1`. The video's local model was `mimo-v2.6:9b-q4_K_M`. To use another company's own class in place of `ChatOpenAI`, change `make_model()` in `app/common.py`.

Three things change with a real model:

- The request log is gone, because a real model doesn't write one.
- The kills in mission 8 that count requests in that log won't work. Use the form that counts rows in `payments`.
- The numbers change. The scripted model always asks for one tool at a time and never makes a mistake. A slow model on the whole job takes hours: `python steps.py s11-cap <thread> 6` ends a payment run after six requests of our agent.

With a local model, the memory step may need a firmer instruction: with `MEMORY_FIRM=1` the lab adds one sentence about the memory file to the agent's instructions (`docker compose exec -T -e MEMORY_FIRM=1 lab python steps.py s7-remember <thread>`).

## Traces in LangSmith

Tracing is off unless you turn it on. LangSmith is a hosted service with a free plan; the lab runs without it. Put your key in a file outside this repository, and start the lab through `tools/traced.sh`:

```bash
mkdir -p ~/.config/langsmith && chmod 700 ~/.config/langsmith     # then put the key in ~/.config/langsmith/api_key
LANGSMITH_PROJECT=juniper-lab PRICE_TRACES=1 tools/traced.sh docker compose up -d --build --wait
```

`tools/traced.sh` reads the key and passes it on for that one command; it never prints it. An account outside the default US region needs its own API address, one line in `~/.config/langsmith/endpoint`: for the EU, `https://eu.api.smith.langchain.com`. Every later `docker compose up` or `docker compose run` goes through `tools/traced.sh` too, and finish with `docker compose down`, so no container keeps the key.

LangSmith prices a call only when it knows the model's name, and it doesn't know the lab's. With `PRICE_TRACES=1`, the lab prices each call at `price-list.json` and sends the dollars with the trace.

## A real embedding model

The policy search uses a stand-in by default: it counts words and knows nothing about meaning, and it says so in its output. A real embedding model is two settings. The video uses `nomic-embed-text` on Ollama: free, 274 MB, Apache License 2.0, a vector of 768 numbers.

```bash
ollama pull nomic-embed-text
EMBEDDING_BASE_URL=http://host.docker.internal:11434 EMBEDDING_MODEL=nomic-embed-text docker compose up -d --wait
docker compose exec -T lab python -m app.policy_index build
docker compose exec -T lab python -m app.policy_index search "who approves a payment"
docker compose exec -T lab python -m app.policy_index compare "does the boss have to agree to an expensive bill"
```

`EMBEDDING_BASE_URL` is Ollama's own address, without `/v1`; the model that answers stays the scripted one. Build the table again after changing the setting: a search refuses a table that another embedding built.

## What is here

| Path | What it holds |
|---|---|
| `agent_by_hand.py` | Missions 1 to 3: the whole agent in one file, with Python's standard library only. The loop is lines 50 to 61. |
| `agent_langchain.py` | Missions 4 and 5: the same agent with `create_agent`, and the long job on it. |
| `agent_by_hand_saved.py` | Mission 8: the hand-written agent with nine lines that keep its list in Postgres. |
| `steps.py` | Missions 6 to 13: one small command for each step. `python steps.py` lists them. |
| `app/payables.py` | The five tools as plain Python functions. They read and write the business database. |
| `app/payables_agent.py` | `build_agent()`: the deep agent, where every later part is one argument. |
| `app/common.py` | The model, and the tools wrapped for LangChain. |
| `app/policy_index.py` | The policy in a vector table, and `search_policy`. |
| `app/receiving_service.py` | The receiving agent: its tool, `POST /ask`, and its A2A endpoints. |
| `app/payables_service.py` | Our agent as a service: start a run, ask where it stands, send a decision. |
| `fake_model/` | The scripted model: `server.py` is the HTTP side and the log, `script.py` is the rules, `tokens.py` counts the tokens. |
| `price-list.json`, `app/pricing.py` | One hosted model's public list price, with its source and date, and the sum that turns tokens into dollars. |
| `seed/` | The two schemas and the data generator. |
| `policy/` | The Juniper Market Accounts Payable Policy, 26 sections. |
| `sql/` | The queries the missions use. |
| `tools/` | `kill-when.sh`, `all-steps.sh`, `dana.py` (approves over HTTP), the log reader `reqlog.py`, `price.py`, `kept.py`, `traced.sh`, `trace.py` (reads traces back from LangSmith) and small fact printers. |
| `requirements.txt`, `constraints.txt` | The pinned packages, and everything they pulled in. |

## Limits to know

- One Postgres server holds all three databases, with no password and no published port. That's fine for a lab and wrong for anything real.
- Nothing stops the payables agent's code from reading the receiving database. It simply has no tool for it.
- The service's token is a fixed lab value in `compose.yaml`. It shows where the check sits, and it protects nothing.
- The scripted model checks every invoice it's given. It doesn't look at the `status` a list of invoices carries, so a run that starts over schedules again what is already scheduled. A real model may read that status.
- Only free and open-source packages are installed. LangSmith's Agent Server, `langgraph dev` and Managed Deep Agents are not used.

## Remove everything

```bash
docker compose down -v --rmi local
```

This removes the containers, the three volumes, the network and the image the lab built. The images it downloaded stay in Docker's cache; `--rmi all` removes those too.
