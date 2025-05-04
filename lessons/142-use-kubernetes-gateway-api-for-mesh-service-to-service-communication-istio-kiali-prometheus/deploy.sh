#!/bin/bash

kubectl create -f prometheus-operator-crd
kubectl create -f istio-crds.yaml
kubectl create -f gateway-exp-crds

kubectl apply -f istio-system-ns.yaml
kubectl apply -f monitoring-ns.yaml

kubectl apply -f istiod

kubectl apply -R -f monitoring
