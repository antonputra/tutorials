## How to create a pod in Kubernetes?

### Set up a local Kubernetes cluster using Minikube

```bash
minikube start
```

### Deploy a standalone pod in Kubernetes

```bash
kubectl apply -f 2-pod/0-pod.yaml
```

### Get the list of pods in the default namespace

```bash
kubectl get pods
```

### Tail the logs from the pod

```bash
kubectl logs -f myapp
```
