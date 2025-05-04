
#!/bin/bash

set -x

# setup default values, use environment variables to override
# for example: export LESSON=lesson147 && ./build.sh
VER="${VER:-latest}"
LESSON="${LESSON:-lesson000}"
TARGET_PLATFORM="${TARGET_PLATFORM:-linux/amd64}"

# go-app
docker build -t aputra/go-app-${LESSON}:${VER} --platform ${TARGET_PLATFORM} go-app
docker push aputra/go-app-${LESSON}:${VER}

# rust-app
docker build -t aputra/rust-app-${LESSON}:${VER} --platform ${TARGET_PLATFORM} rust-app
docker push aputra/rust-app-${LESSON}:${VER}
