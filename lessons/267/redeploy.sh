#!/bin/bash

set -xe

echo new_tag: $1

cd lambda

docker buildx build --platform linux/arm64 --provenance=false -t 424432388155.dkr.ecr.ap-northeast-1.amazonaws.com/mexc/market-maker:$1 .

docker push 424432388155.dkr.ecr.ap-northeast-1.amazonaws.com/mexc/market-maker:$1

cd ../terraform

terraform apply --auto-approve -var "tag=$1"
