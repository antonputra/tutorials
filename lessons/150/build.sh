
#!/bin/bash

set -x

# setup default values, use environment variables to override
# for example: export LESSON=lesson150 && ./build.sh
VER="${VER:-latest}"
LESSON="${LESSON:-lesson000}"

# go-app amd64
docker build -t aputra/go-app-amd64-${LESSON}:${VER} --platform linux/amd64 go-app
docker push aputra/go-app-amd64-${LESSON}:${VER}

# go-app arm64
docker build -t aputra/go-app-arm64-${LESSON}:${VER} --platform linux/arm64 go-app
docker push aputra/go-app-arm64-${LESSON}:${VER}
