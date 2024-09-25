#!/usr/bin/env bash

set -x

# To run, execute: ./build.sh go-app v1
USERNAMR="${USERNAMR:-aputra}"
LESSON=$(basename $(pwd))
DOCKERFILE="${DOCKERFILE:-Dockerfile}"
APP_DIR="$1"
VER="$2"

docker build -t ${USERNAMR}/${APP_DIR}-${LESSON}-arm64:${VER} -f ${APP_DIR}/${DOCKERFILE} --platform linux/arm64 ${APP_DIR}
docker build -t ${USERNAMR}/${APP_DIR}-${LESSON}-amd64:${VER} -f ${APP_DIR}/${DOCKERFILE} --platform linux/amd64 ${APP_DIR}

docker push ${USERNAMR}/${APP_DIR}-${LESSON}-arm64:${VER}
docker push ${USERNAMR}/${APP_DIR}-${LESSON}-amd64:${VER}

docker manifest create ${USERNAMR}/${APP_DIR}-${LESSON}:${VER} \
    ${USERNAMR}/${APP_DIR}-${LESSON}-arm64:${VER} \
    ${USERNAMR}/${APP_DIR}-${LESSON}-amd64:${VER}

docker manifest push ${USERNAMR}/${APP_DIR}-${LESSON}:${VER}
