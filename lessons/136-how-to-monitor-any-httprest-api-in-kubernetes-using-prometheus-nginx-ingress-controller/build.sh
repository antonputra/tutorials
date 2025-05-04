#!/bin/bash

set -e

docker build -t 424432388155.dkr.ecr.us-east-1.amazonaws.com/my-app:latest --platform linux/amd64 my-app
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 424432388155.dkr.ecr.us-east-1.amazonaws.com
docker push 424432388155.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

kubectl rollout restart deployment my-app -n staging
kubectl rollout restart deployment hardware -n production
kubectl rollout restart deployment login -n production
