# AI Agents: Try It Yourself

You can find tutorial [here](https://youtu.be/_emAwgng9xc).

This is the exercise for my video about how AI agents work. You run the payment agent from the video on your own computer, and kill it in the middle of its Friday payment run. With nothing saved, it starts over and pays 18 invoices twice. With every step saved in Postgres, it carries on from invoice 23 and pays each invoice once. It takes about 15 minutes. The page with the expected output of every step is https://antonputra.com/exercises/ai-agents/.

You need Git and Docker (start Docker Desktop first, or the Docker service on Linux) and about 4 GB of free disk space. Nothing else: no Python on your computer, no account and no key. Run the commands in a terminal: Terminal on a Mac, your shell on Linux, and on Windows a WSL terminal, such as Ubuntu, with Docker Desktop's WSL integration turned on. On Linux, add your user to the `docker` group first, as Docker's install guide shows: the script that kills the agent runs `docker` itself.

The exercise runs on the full lab's code, in the `lab` folder next to this file. The model there is the scripted stand-in from the video's long runs: a few rules in a container, not a real model. It gets what a model gets, the messages and the tools on offer, and answers in the same format, so the agent's code can't tell the difference. That's why you need no account and no key, and why you get the video's numbers. The full lab, every step of the video, is on https://antonputra.com/labs/ai-agents/.

## 1. Start the lab

```bash
cd lab
docker compose up -d --build --wait
```

The first start builds the lab's image: it downloads Python, Postgres with pgvector, and the Python packages, LangChain, LangGraph and Deep Agents among them, so give it a few minutes. When the command returns, everything is ready: Postgres with the data of Juniper Market, the small grocery store from the video, the scripted model, and a container named `lab`, where the agent runs. No port is published.

The data is the video's: 40 supplier invoices, numbers 1031 to 1070, all due on Friday, November 27, 2026. `docker compose exec -T lab` in front of a command runs it in the `lab` container.

## 2. Ask about one invoice

The agent from the start of the video is the loop of twelve lines in `agent_by_hand.py`, with no library. Ask it about invoice 1042:

```bash
docker compose exec -T lab python agent_by_hand.py loop
```

Three requests, two tools: the model asks for the invoice and the purchase order, and our code reads them from the database. The answer: the invoice bills 55 cases of paper cups where the order has 50, $190.00 too much, and a $60.00 freight line that is on no purchase order.

## 3. Kill it, with nothing saved

The whole Friday run, with each invoice handed to a helper. This version saves nothing. Start it in a container of its own, with the model slowed down to half a second a reply, then kill it in the middle of invoice 23:

```bash
docker compose exec -T lab python -m seed.seed --reset-activity
docker compose exec -T lab python -m app.control s5-nosave-first
docker compose run -d --name payrun-n lab python steps.py s5-nosave first 500 helpers
tools/kill-when.sh payrun-n 114 'docker exec juniper-lab-fake-model-1 sh -c "ls /logs/s5-nosave-first 2>/dev/null | grep -c request; true"'
docker rm payrun-n
```

The first line empties the payments and the holds. The second empties the model's request log, which `kill-when.sh` counts: at 114 requests, about a minute in, it kills the container with SIGKILL, exit code 137. The last line removes the stopped container. Look at the payments, then start it again:

```bash
docker compose exec -T postgres psql -U postgres -d juniper < sql/payments.sql
docker compose exec -T lab python steps.py s5-nosave again 0 helpers
docker compose exec -T postgres psql -U postgres -d juniper < sql/payments.sql
```

18 payments when it died. Started again, it begins at invoice 1031, the first one, and ends with 51 payments for 33 invoices: the 18 paid before the kill are paid twice, $232,581.50 where $151,275.00 was due.

## 4. Kill it, with every step saved

The same agent, with LangGraph saving every step in Postgres under the run's name, `friday`. Kill it in the same place, and start it again with the same name:

```bash
docker compose exec -T lab python -m seed.seed --reset-activity
docker compose exec -T lab python -m app.control s8-friday
docker compose run -d --name payrun-s lab python steps.py s8-delegate friday 500
tools/kill-when.sh payrun-s 114 'docker exec juniper-lab-fake-model-1 sh -c "ls /logs/s8-friday 2>/dev/null | grep -c request; true"'
docker rm payrun-s
docker compose exec -T lab python steps.py s8-delegate friday
docker compose exec -T postgres psql -U postgres -d juniper < sql/payments.sql
docker compose exec -T lab python -m tools.reqlog same s8-friday 114 115
```

It finds 92 messages saved, with the tools as the next stop: our agent had just handed invoice 1053, number 23, to a helper. It carries on from there and ends with 33 payments for 33 invoices. One request to the model ran twice, byte for byte; no tool did. If `kill-when.sh` said `count is 115`, compare 115 and 116.

## Extra: the worst moment to die

Kill it inside the payment tool, after the payment's row is written and before the step is saved: `PAYMENT_CONFIRM_SECONDS=2` makes the tool wait two seconds after its write, and `kill-when.sh` counts the payments this time:

```bash
docker compose exec -T lab python -m seed.seed --reset-activity
docker compose run -d --name payrun-t -e PAYMENT_CONFIRM_SECONDS=2 lab python steps.py s8-delegate friday-t
tools/kill-when.sh payrun-t 8 'docker compose exec -T postgres psql -U postgres -d juniper -Atc "select count(*) from payments"'
docker rm payrun-t
docker compose exec -T lab python steps.py s8-delegate friday-t
docker compose exec -T postgres psql -U postgres -d juniper < sql/payments.sql
```

Invoice 1039, $5,721.00, is paid twice. With a key on each payment, `PAYMENTS_IDEMPOTENT=1`, the tool looks for the key before it writes:

```bash
docker compose exec -T lab python -m seed.seed --reset-activity
docker compose run -d --name payrun-u -e PAYMENT_CONFIRM_SECONDS=2 -e PAYMENTS_IDEMPOTENT=1 lab python steps.py s8-delegate friday-u
tools/kill-when.sh payrun-u 8 'docker compose exec -T postgres psql -U postgres -d juniper -Atc "select count(*) from payments"'
docker rm payrun-u
docker compose exec -T -e PAYMENTS_IDEMPOTENT=1 lab python steps.py s8-delegate friday-u
docker compose exec -T postgres psql -U postgres -d juniper < sql/payments.sql
```

The tool runs twice for invoice 1039, and writes once.

## 5. Clean up

```bash
docker compose down -v --rmi local
```

It removes the lab's containers, its three volumes and the image it built. Then you can delete the `tutorials` folder.

| The Friday run | Payments | For invoices | Paid |
|---|---|---|---|
| What was due | 33 | 33 | $151,275.00 |
| Killed in invoice 23, nothing saved | 51 | 33 | $232,581.50 |
| Killed in invoice 23, every step saved | 33 | 33 | $151,275.00 |
| Killed inside the payment for invoice 1039 | 34 | 33 | $156,996.00 |
| The same, with a key on each payment | 33 | 33 | $151,275.00 |
