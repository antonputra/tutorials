#!/usr/bin/env bash

# Print the commands.
set -x

# Exit script on error.
set -e

# To run, execute: ./build.sh go-app v1
USERNAMR="${USERNAMR:-aputra}"
PROVIDER="${PROVIDER:-docker.io}"
LESSON=$(basename $(pwd))
DOCKERFILE="${DOCKERFILE:-Dockerfile}"
APP_DIR="$1"
VER="$2"
DOCKERFILE="$3"

docker build -t ${PROVIDER}/${USERNAMR}/${APP_DIR}-${LESSON}-arm64:${VER} -f ${APP_DIR}/${DOCKERFILE} --platform linux/arm64 ${APP_DIR}
docker build -t ${PROVIDER}/${USERNAMR}/${APP_DIR}-${LESSON}-amd64:${VER} -f ${APP_DIR}/${DOCKERFILE} --platform linux/amd64 ${APP_DIR}

docker push ${PROVIDER}/${USERNAMR}/${APP_DIR}-${LESSON}-arm64:${VER}
docker push ${PROVIDER}/${USERNAMR}/${APP_DIR}-${LESSON}-amd64:${VER}

docker manifest create ${PROVIDER}/${USERNAMR}/${APP_DIR}-${LESSON}:${VER} \
    ${PROVIDER}/${USERNAMR}/${APP_DIR}-${LESSON}-arm64:${VER} \
    ${PROVIDER}/${USERNAMR}/${APP_DIR}-${LESSON}-amd64:${VER}

docker manifest push ${PROVIDER}/${USERNAMR}/${APP_DIR}-${LESSON}:${VER}
