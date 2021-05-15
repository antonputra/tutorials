# Kubernetes Network Policy Examples & Tutorial (Calico Isolate Namespaces, Pods & IP Blocks)

[YouTube Tutorial](https://youtu.be/bVeM33B2f1A)

## Create EKS cluster
```bash
eksctl create cluster -f eks.yaml
```

## Installing Calico on Amazon EKS
Apply the Calico manifests
```bash
kubectl apply -f https://raw.githubusercontent.com/aws/amazon-vpc-cni-k8s/master/config/master/calico-operator.yaml
kubectl apply -f https://raw.githubusercontent.com/aws/amazon-vpc-cni-k8s/master/config/master/calico-crs.yaml
```
Watch the calico-system DaemonSets
```bash
kubectl get daemonset calico-node -n calico-system
```

## Create Services

## Check Connection
```bash
kubectl exec service-a-<id> -n staging -- nc -vz service-b 8080
kubectl get pods --show-labels
kubectl exec service-a-<id> -n staging -- nc -vz service-c.production 8080
```