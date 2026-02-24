#!/bin/bash

REPLICAS=10
SLEEP=10

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Applying with REPLICAS=$REPLICAS"

    export REPLICAS=$REPLICAS

    envsubst < test/clients.yaml | kubectl apply -f -

    echo "Sleeping ${SLEEP} seconds..."

    sleep ${SLEEP}
    ((REPLICAS++))
done
