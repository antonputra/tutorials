#!/bin/bash

set -ex

# Create Custom Resource Definitions

kubectl create -f prometheus-operator-crd

# Create Kubernetes Namespaces

kubectl apply -f namespaces

# Deploy Monitoring Components

kubectl apply -R -f monitoring

# Deploy Applications
