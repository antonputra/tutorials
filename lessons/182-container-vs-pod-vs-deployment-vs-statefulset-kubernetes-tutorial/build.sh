#!/usr/bin/env bash

set -x

# setup default values, use environment variables to override
# export VER=v1 APP_DIR=myapp && ./build.sh
USERNAMR="${USERNAMR:-aputra}"
VER="${VER:-latest}"
LESSON=$(basename $(pwd))
APP_DIR="${APP_DIR:-0}"
APP_NAME="${APP_NAME:-myapp}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"

# service-a
docker build -t ${USERNAMR}/${APP_NAME}-${LESSON}-arm64:${VER} -f ${APP_DIR}/${DOCKERFILE} --platform linux/arm64 ${APP_DIR}
docker build -t ${USERNAMR}/${APP_NAME}-${LESSON}-amd64:${VER} -f ${APP_DIR}/${DOCKERFILE} --platform linux/amd64 ${APP_DIR}

docker push ${USERNAMR}/${APP_NAME}-${LESSON}-arm64:${VER}
docker push ${USERNAMR}/${APP_NAME}-${LESSON}-amd64:${VER}

docker manifest create ${USERNAMR}/${APP_NAME}-${LESSON}:${VER} \
    ${USERNAMR}/${APP_NAME}-${LESSON}-arm64:${VER} \
    ${USERNAMR}/${APP_NAME}-${LESSON}-amd64:${VER}

docker manifest push ${USERNAMR}/${APP_NAME}-${LESSON}:${VER}
