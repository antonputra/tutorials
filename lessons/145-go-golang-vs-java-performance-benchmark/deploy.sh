#!/bin/bash

set -ex

# Create Custom Resource Definitions

kubectl create -f prometheus-operator-crd

# Create Kubernetes Namespaces

kubectl apply -f namespaces

# Deploy Monitoring Components

kubectl apply -R -f monitoring

# Deploy db and s3

kubectl apply -f mongodb
kubectl apply -f minio

# Deploy Applications

kubectl apply -f java-app/deploy
kubectl apply -f go-app/deploy
