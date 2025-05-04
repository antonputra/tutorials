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

# go-app
docker build -t ${ACC}.dkr.ecr.${REGION}.amazonaws.com/go-app:${VER} --platform ${TARGET_PLATFORM} go-app
docker push ${ACC}.dkr.ecr.${REGION}.amazonaws.com/go-app:${VER}

# java-app
docker build -t ${ACC}.dkr.ecr.${REGION}.amazonaws.com/java-app:${VER} --platform ${TARGET_PLATFORM} java-app
docker push ${ACC}.dkr.ecr.${REGION}.amazonaws.com/java-app:${VER}
