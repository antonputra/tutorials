# Helm 3 Tutorial (Create Helm 3 Hello World Example)

### Create Kubernetes Cluster (Optional)
```bash
$ eksctl create cluster -f lessons/021/eksctl-cluster.yaml
$ kubectl get svc -n default
```

### Initialize a Helm Chart Repository
```bash
$ helm repo add stable https://charts.helm.sh/stable
```

### List Available Charts
```bash
$ helm search repo stable
```

### Create Hello-world Example
```bash
$ helm create hello-wolrd
```

### Install Hello-worls Helm Chart
```bash
$ kubectl create namespace dev
$ helm install -f hello-wolrd/values.yaml -n dev hello-wolrd ./hello-wolrd
```

### Learn About hello-world Release
```bash
$ helm ls -n dev
```

### Get Pods, Services
```bash
$ kubectl get pods -n dev
$ kubectl get services -n dev
```

### Clean Up

```bash
# Uninstall a Release
$ helm uninstall -n dev hello-wolrd

# remove stable repo
$ helm repo remove stable
```
