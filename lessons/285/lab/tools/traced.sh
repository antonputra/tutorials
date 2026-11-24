#!/bin/bash
# tools/traced.sh <command ...>: run one command with LangSmith tracing switched on for every docker compose call in it.
#
#   tools/traced.sh docker compose up -d --build --wait      start the lab with traces on
#   tools/traced.sh docker compose run --rm lab python ...   a container of its own, traced like the others
#
# The key is read from a file outside this repository and handed to the command in its environment. It is never
# printed and never written anywhere. Containers started this way hold it in their environment until they are removed.
#   LANGSMITH_KEY_FILE            the key's file, default ~/.config/langsmith/api_key
#   <that folder>/endpoint        optional: the API address of your region, one line (the default is the US region)
#   LANGSMITH_PROJECT             the tracing project's name, default juniper-lab
#   LANGSMITH_AGENT_ID and LANGSMITH_AGENT_ENVIRONMENT   in an agent-based workspace, instead of a project
#   PRICE_TRACES=1                also price each call's tokens at price-list.json
set -euo pipefail
[ $# -gt 0 ] || { echo "usage: tools/traced.sh <command ...>" >&2; exit 2; }
KEY_FILE="${LANGSMITH_KEY_FILE:-$HOME/.config/langsmith/api_key}"
[ -f "$KEY_FILE" ] || { echo "traced: no key file at $KEY_FILE" >&2; exit 2; }
LANGSMITH_API_KEY="$(tr -d ' \r\n' < "$KEY_FILE")"
[ -n "$LANGSMITH_API_KEY" ] || { echo "traced: the key file is empty" >&2; exit 2; }
ENDPOINT_FILE="$(dirname "$KEY_FILE")/endpoint"
if [ -z "${LANGSMITH_ENDPOINT:-}" ] && [ -f "$ENDPOINT_FILE" ]; then LANGSMITH_ENDPOINT="$(tr -d ' \r\n' < "$ENDPOINT_FILE")"; fi
LANGSMITH_ENDPOINT="${LANGSMITH_ENDPOINT:-https://api.smith.langchain.com}"
LANGSMITH_TRACING=true
export LANGSMITH_API_KEY LANGSMITH_ENDPOINT LANGSMITH_TRACING
if [ -z "${LANGSMITH_AGENT_ID:-}" ]; then export LANGSMITH_PROJECT="${LANGSMITH_PROJECT:-juniper-lab}"; fi
exec "$@"
