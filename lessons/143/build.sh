#!/bin/bash

set -x

# setup default values, use environment variables to override
# for example: export VER=0.1.0 && ./build.sh
VER="${VER:-latest}"
REGION="${REGION:-us-east-1}"
ACC="${ACC:-424432388155}"
TARGET_PLATFORM="${TARGET_PLATFORM:-linux/amd64}"

# authenticate with aws
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACC}.dkr.ecr.${REGION}.amazonaws.com

# golang service-a
docker build -t ${ACC}.dkr.ecr.${REGION}.amazonaws.com/go-app:service-a-${VER} --platform ${TARGET_PLATFORM} -f go-app/service-a.Dockerfile go-app
docker push ${ACC}.dkr.ecr.${REGION}.amazonaws.com/go-app:service-a-${VER}

# golang service-b
docker build -t ${ACC}.dkr.ecr.${REGION}.amazonaws.com/go-app:service-b-${VER} --platform ${TARGET_PLATFORM} -f go-app/service-b.Dockerfile go-app
docker push ${ACC}.dkr.ecr.${REGION}.amazonaws.com/go-app:service-b-${VER}

# node service-a
docker build -t ${ACC}.dkr.ecr.${REGION}.amazonaws.com/node-app:service-a-${VER} --platform ${TARGET_PLATFORM} -f node-app/service-a.Dockerfile node-app
docker push ${ACC}.dkr.ecr.${REGION}.amazonaws.com/node-app:service-a-${VER}

# node service-b
docker build -t ${ACC}.dkr.ecr.${REGION}.amazonaws.com/node-app:service-b-${VER} --platform ${TARGET_PLATFORM} -f node-app/service-b.Dockerfile node-app
docker push ${ACC}.dkr.ecr.${REGION}.amazonaws.com/node-app:service-b-${VER}
