#!/bin/bash

kubectl apply -f go-app/deploy/0-namespace.yaml
kubectl apply -f go-app/deploy/1-deployment-service-a.yaml
kubectl apply -f go-app/deploy/2-service-a.yaml
kubectl apply -f go-app/deploy/3-deployment-service-b-v1.yaml
kubectl apply -f go-app/deploy/4-deployment-service-b-v2.yaml
kubectl apply -f go-app/deploy/5-service-b.yaml
kubectl apply -f go-app/deploy/6-pod-monitor.yaml
