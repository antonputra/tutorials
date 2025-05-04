#!/bin/bash

set -x

# setup default values, use environment variables to override
# for example: export LESSON=171 VER=v1 && ./build.sh
VER="${VER:-latest}"
LESSON="${LESSON:-0}"

# service-a
docker build -t aputra/service-a-${LESSON}-arm64:${VER} -f myapp/service-a.Dockerfile --platform linux/arm64 myapp
docker build -t aputra/service-a-${LESSON}-amd64:${VER} -f myapp/service-a.Dockerfile --platform linux/amd64 myapp

docker push aputra/service-a-${LESSON}-arm64:${VER}
docker push aputra/service-a-${LESSON}-amd64:${VER}

docker manifest create aputra/service-a-${LESSON}:${VER} \
    aputra/service-a-${LESSON}-arm64:${VER} \
    aputra/service-a-${LESSON}-amd64:${VER}

docker manifest push aputra/service-a-${LESSON}:${VER}

# service-b
docker build -t aputra/service-b-${LESSON}-arm64:${VER} -f myapp/service-b.Dockerfile --platform linux/arm64 myapp
docker build -t aputra/service-b-${LESSON}-amd64:${VER} -f myapp/service-b.Dockerfile --platform linux/amd64 myapp

docker push aputra/service-b-${LESSON}-arm64:${VER}
docker push aputra/service-b-${LESSON}-amd64:${VER}

docker manifest create aputra/service-b-${LESSON}:${VER} \
    aputra/service-b-${LESSON}-arm64:${VER} \
    aputra/service-b-${LESSON}-amd64:${VER}

docker manifest push aputra/service-b-${LESSON}:${VER}

# client
docker build -t aputra/client-${LESSON}-arm64:${VER} -f client/Dockerfile --platform linux/arm64 client
docker build -t aputra/client-${LESSON}-amd64:${VER} -f client/Dockerfile --platform linux/amd64 client

docker push aputra/client-${LESSON}-arm64:${VER}
docker push aputra/client-${LESSON}-amd64:${VER}

docker manifest create aputra/client-${LESSON}:${VER} \
    aputra/client-${LESSON}-arm64:${VER} \
    aputra/client-${LESSON}-amd64:${VER}

docker manifest push aputra/client-${LESSON}:${VER}
