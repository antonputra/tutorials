#!/bin/bash

set -ex

aws eks update-kubeconfig --name demo --region us-east-1

# Create Custom Resource Definitions

kubectl create -f prometheus-operator-crd

# Create Kubernetes Namespaces

kubectl apply -f namespaces

# Deploy Monitoring Components

kubectl apply -R -f monitoring

# Deploy Zookeeper

kubectl apply -f zookeeper

# Deploy Kafka

kubectl apply -f kafka

# Deploy kafka client

kubectl apply -f kafka-client.yaml

# Create topic for benchmark

kubectl exec -n staging kafka-client -- kafka-topics.sh --create --topic benchmark --replication-factor 3 --partitions 12  --bootstrap-server kafka-headless.kafka:9092

# Deploy Application

kubectl apply -R -f app/deploy/
