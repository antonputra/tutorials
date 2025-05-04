# Kubernetes Namespaces vs. Virtual Clusters

[YouTube Tutorial](https://youtu.be/IP64cimwwgM)


## Install vcluster

```bash
vcluster create vcluster-1 -n host-namespace-1
vcluster connect vcluster-1 --namespace host-namespace-1
kubectl get namespace
kubectl create namespace demo-nginx
kubectl create deployment nginx-deployment -n demo-nginx --image=nginx
kubectl get pods -n demo-nginx
kubectl get deployment -n host-namespace-1
kubectl get pods -n host-namespace-1
```

## Links

- [vcluster - GitHub](https://github.com/loft-sh/vcluster)
- [vcluster - getting-started](https://www.vcluster.com/docs/getting-started/setup)
- [K3s](https://k3s.io/)
