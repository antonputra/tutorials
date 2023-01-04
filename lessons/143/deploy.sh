#!/bin/bash

set -ex

kubectl create -f prometheus-operator-crd
kubectl create -f istio-crds.yaml
kubectl create -f gateway-exp-crds

kubectl apply -f istio-system-ns.yaml
kubectl apply -f monitoring-ns.yaml
kubectl apply -f minio-ns.yaml
kubectl apply -f monitoring-ns.yaml
kubectl apply -f golang-ns.yaml
kubectl apply -f nodejs-ns.yaml
kubectl apply -f mongodb-ns.yaml
kubectl apply -f gateway-ns.yaml

kubectl apply -R -f monitoring

kubectl apply -f istiod
kubectl apply -f minio
kubectl apply -f gateway
kubectl apply -f mongodb

kubectl apply -f istio-sidecars-pod-monitor.yaml
kubectl apply -f gateway-api-pod-monitor.yaml

kubectl apply -R -f go-app/deploy
kubectl apply -R -f node-app/deploy
