#!/bin/bash

set -x

# setup default values, use environment variables to override
# for example: export LESSON=lesson150 && ./build.sh
VER="${VER:-latest}"
LESSON="${LESSON:-lesson000}"

# myapp
docker build -t aputra/myapp-${LESSON}:${VER} -f myapp/Dockerfile --platform linux/amd64 myapp
docker push aputra/myapp-${LESSON}:${VER}
