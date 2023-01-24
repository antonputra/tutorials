#!/bin/bash

set -x

# setup default values, use environment variables to override
# for example: export LESSON=lesson147 && ./build.sh
VER="${VER:-latest}"
LESSON="${LESSON:-lesson000}"
TARGET_PLATFORM="${TARGET_PLATFORM:-linux/amd64}"

# grpc
docker build -t aputra/grpc-${LESSON}:${VER} --platform ${TARGET_PLATFORM} -f app/grpc.Dockerfile app
docker push aputra/grpc-${LESSON}:${VER}

# rest
docker build -t aputra/rest-${LESSON}:${VER} --platform ${TARGET_PLATFORM} -f app/rest.Dockerfile app
docker push aputra/rest-${LESSON}:${VER}
