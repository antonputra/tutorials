#!/bin/bash
# tools/kill-when.sh <container> <number> '<command that prints a count>'
# Poll the command; when the count reaches the number, send SIGKILL to the container (docker kill).
# The process gets no chance to save anything: this is a crash, not a shutdown.
set -uo pipefail
NAME="$1"; AT="$2"; PROBE="$3"
for _ in $(seq 100); do     # wait until the container runs
  [ "$(docker inspect -f '{{.State.Running}}' "$NAME" 2>/dev/null)" = "true" ] && break
  sleep 0.1
done
while :; do
  OUT="$(bash -c "$PROBE" 2>&1)" || { echo "the count command failed: $OUT"; exit 2; }
  N="$(printf '%s' "$OUT" | tr -dc '0-9')"
  [ "${N:-0}" -ge "$AT" ] && break
  [ "$(docker inspect -f '{{.State.Running}}' "$NAME" 2>/dev/null)" = "true" ] || { echo "the container stopped before the count reached $AT (count ${N:-0})"; exit 1; }
  sleep 0.2
done
echo "$(date -u +%H:%M:%S) count is $N: docker kill $NAME"
docker kill "$NAME" >/dev/null
sleep 0.5
docker inspect -f 'container {{.Name}}: {{.State.Status}}, exit code {{.State.ExitCode}}, finished {{.State.FinishedAt}}' "$NAME"
