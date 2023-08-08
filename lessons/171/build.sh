#!/bin/bash

set -x

# setup default values, use environment variables to override
# for example: export LESSON=171 VER=v1 && ./build.sh
VER="${VER:-latest}"
LESSON="${LESSON:-0}"

# myapp
docker build -t aputra/myapp-${LESSON}-arm64:${VER} -f myapp/Dockerfile --platform linux/arm64 myapp
docker build -t aputra/myapp-${LESSON}-amd64:${VER} -f myapp/Dockerfile --platform linux/amd64 myapp

docker push aputra/myapp-${LESSON}-arm64:${VER}
docker push aputra/myapp-${LESSON}-amd64:${VER}

docker manifest create aputra/myapp-${LESSON}:${VER} \
    aputra/myapp-${LESSON}-arm64:${VER} \
    aputra/myapp-${LESSON}-amd64:${VER}

docker manifest push aputra/myapp-${LESSON}:${VER}
