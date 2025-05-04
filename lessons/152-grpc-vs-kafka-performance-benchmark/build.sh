
#!/bin/bash

set -x

# setup default values, use environment variables to override
# for example: export LESSON=lesson150 && ./build.sh
VER="${VER:-latest}"
LESSON="${LESSON:-lesson000}"

# kafka-agent
docker build -t aputra/kafka-agent-${LESSON}:${VER} -f app/kafka-agent.Dockerfile --platform linux/amd64 app
docker push aputra/kafka-agent-${LESSON}:${VER}

# grpc-server
docker build -t aputra/grpc-server-${LESSON}:${VER} -f app/grpc-server.Dockerfile --platform linux/amd64 app
docker push aputra/grpc-server-${LESSON}:${VER}

# grpc-client
docker build -t aputra/grpc-client-${LESSON}:${VER} -f app/grpc-client.Dockerfile --platform linux/amd64 app
docker push aputra/grpc-client-${LESSON}:${VER}
