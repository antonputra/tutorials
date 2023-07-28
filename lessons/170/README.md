# Kubernetes Node Selector vs Node Affinity vs Pod Affinity vs Tains & Tolerations

You can find tutorial [here](https://youtu.be/rX4v_L0k4Hc).

## Start minikube with 3 nodes

```bash
minikube start --nodes 3 --driver=docker
```

## Get Kubernetes node labels

```bash
kubectl get node --show-labels
```

## Set the node label

```bash
# kubectl label nodes <node> <label-key>=<label-value>
kubectl label nodes minikube-m03 disktype=ssd
```

## Set the node taint

```bash
# kubectl taint nodes <node> <taint-key>=<taint-value>:<taint-effect>
kubectl taint nodes minikube-m03 price=spot:NoSchedule
```


## Links

- [Kubernetes Scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [Scheduler Performance Tuning](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduler-perf-tuning/)
- [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
