#!/bin/bash

set -ex

aws eks update-kubeconfig --name demo-arm64 --region us-east-1

# Create Custom Resource Definitions

kubectl create -f prometheus-operator-crd

# Create Kubernetes Namespaces

kubectl apply -f namespaces

# Deploy Monitoring Components

kubectl apply -R -f monitoring
kubectl apply -f prometheus-arm64
kubectl apply -f node-exporter-arm64

# Deploy Application

kubectl apply -f go-app/deploy/arm64
