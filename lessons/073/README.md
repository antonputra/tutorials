# Horizontal Pod Autoscaler CUSTOM METRICS & PROMETHEUS

[YouTube Tutorial](https://youtu.be/iodq-4srXA8)

# Steps

## 1. Run Sample App Locally

- Go over express app `0-express`
- Open 2 tabs and run it locally
```
node 0-express/server.js
```
> Server listening at http://0.0.0.0:8081
```
curl localhost:8081/fibonacci \
    -H "Content-Type: application/json" \
    -d '{"number": 10}'
```
> Fibonacci number is 89!
```
curl localhost:8081/fibonacci \
    -H "Content-Type: application/json" \
    -d '{"number": 20}'
```
> Fibonacci number is 10946!
```
curl localhost:8081/metrics
```
> \# HELP http_requests_total Total number of http requests  
> \# TYPE http_requests_total counter  
> \# http_requests_total{method="POST"} 2

## 2. Create EKS Cluster Using eksctl
- Open `eks.yaml` file and create EKS cluster
```
eksctl create cluster -f eks.yaml
```
> 2021-06-26 18:22:20 [ℹ]  nodegroup "general" has 1 node(s)  
> 2021-06-26 18:22:20 [ℹ]  node "ip-192-168-11-151.ec2.internal" is ready  
> 2021-06-26 18:24:23 [ℹ]  kubectl command should work with "/Users/antonputra/.kube/config", try 'kubectl get nodes'  
> 2021-06-26 18:24:23 [✔]  EKS cluster "my-cluster-v4" in "us-east-1" region is ready
## 3. Create Namespaces in Kubernetes
- Create `demo` and `monitoring` namespaces
```
kubectl apply -f 1-namespaces
```
> namespace/demo created  
> namespace/monitoring created

## 4. Create Prometheus Operator CRDs
- Create Prometheus CRDs and RBAC
```
kubectl apply -f 2-prometheus-operator-crd
```
> clusterrole.rbac.authorization.k8s.io/prometheus-crd-view created  
> clusterrole.rbac.authorization.k8s.io/prometheus-crd-edit created  
> customresourcedefinition.apiextensions.k8s.io/alertmanagerconfigs.monitoring.coreos.com created  
> customresourcedefinition.apiextensions.k8s.io/alertmanagers.monitoring.coreos.com created  
> customresourcedefinition.apiextensions.k8s.io/podmonitors.monitoring.coreos.com created  
> customresourcedefinition.apiextensions.k8s.io/probes.monitoring.coreos.com created  
> customresourcedefinition.apiextensions.k8s.io/prometheuses.monitoring.coreos.com created  
> customresourcedefinition.apiextensions.k8s.io/prometheusrules.monitoring.coreos.com created  
> customresourcedefinition.apiextensions.k8s.io/servicemonitors.monitoring.coreos.com created  
> customresourcedefinition.apiextensions.k8s.io/thanosrulers.monitoring.coreos.com created  

## 5. Deploy Prometheus Operator on Kubernetes
```
kubectl apply -f 3-prometheus-operator
```
> serviceaccount/prometheus-operator created  
> clusterrole.rbac.authorization.k8s.io/prometheus-operator created  
> clusterrolebinding.rbac.authorization.k8s.io/prometheus-operator created  
> deployment.apps/prometheus-operator created  
> service/prometheus-operator created  
```
kubectl get pods -n monitoring
```
> NAME                                   READY   STATUS    RESTARTS   AGE  
prometheus-operator-585f487768-745xp   1/1     Running   0          11m  
```
kubectl logs -l app.kubernetes.io/name=prometheus-operator -f -n monitoring
```
> level=info ts=2021-06-27T01:44:00.696399754Z caller=operator.go:355 component=prometheusoperator msg="successfully synced all caches"  
> level=info ts=2021-06-27T01:44:00.702534377Z caller=operator.go:267 component=thanosoperator msg="successfully synced all caches"  
> level=info ts=2021-06-27T01:44:00.79632208Z caller=operator.go:287 component=alertmanageroperator msg="successfully synced all caches"  

## 6. Deploy Prometheus on Kubernetes
```
kubectl apply -f 4-prometheus
```
> serviceaccount/prometheus created  
> clusterrole.rbac.authorization.k8s.io/prometheus created  
> clusterrolebinding.rbac.authorization.k8s.io/prometheus created  
> prometheus.monitoring.coreos.com/prometheus created  
```
kubectl get pods -n monitoring
```
> NAME                                   READY   STATUS    RESTARTS   AGE  
prometheus-operator-585f487768-745xp   1/1     Running   0          11m  
prometheus-prometheus-0                2/2     Running   1          5m17s  
```
kubectl logs -l app.kubernetes.io/instance=prometheus -f -n monitoring
```
> level=info ts=2021-06-27T01:50:04.190Z caller=main.go:995 msg="Completed loading of configuration file" filename=/etc/prometheus/config_out/prometheus.env.yaml totalDuration=507.082µs remote_storage=3.213µs web_handler=388ns query_engine=1.274µs scrape=74.372µs scrape_sd=3.853µs notify=996ns notify_sd=1.554µs rules=34.528µs  

## 7. Deploy Sample Express App
- Open Prometheus Target page
```
kubectl port-forward svc/prometheus-operated 9090 -n monitoring
```
> Forwarding from 127.0.0.1:9090 -> 9090  
> Forwarding from [::1]:9090 -> 9090  
- Go to http://localhost:9090
- Use `http` to query Prometheus (empty)

- Create following files
  - `5-demo/0-deployment.yaml`
  - `5-demo/1-service.yaml`
  - `5-demo/2-service-monitor.yaml`
  - `5-demo/3-hpa-http-requests.yaml`
```
kubectl apply -f 5-demo
```
> deployment.apps/express created  
> service/express created  
> servicemonitor.monitoring.coreos.com/express created  
> horizontalpodautoscaler.autoscaling/http created  

- Go back to `http://localhost:9090` target page
- Port forward express app
```
kubectl port-forward svc/express 8081 -n demo
```
- Use curl to hit fibonacci enpont twice
```
curl localhost:8081/fibonacci \
    -H "Content-Type: application/json" \
    -d '{"number": 10}'
```
> Fibonacci number is 89!  
- Use `http` to query Prometheus
- Get hpa
```
kubectl get hpa -n demo
```
> <unknown>/500m  
```
kubectl describe hpa http -n demo
```
```
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1 | jq
```
> Error from server (NotFound): the server could not find the requested resource  

## Deploy Prometheus Adapter

- Create following files
  - `6-prometheus-adapter/0-rbac.yaml`
  - `6-prometheus-adapter/1-deployment.yaml`
  - `6-prometheus-adapter/2-service.yaml`
  - `6-prometheus-adapter/3-apiservice.yaml`
  - `6-prometheus-adapter/4-configmap.yaml` (only 1 rule)
- Run PromQL `http_requests_total{namespace!="",pod!=""}` query
- Deploy Prometheus Adapter
```
kubectl apply -f 6-prometheus-adapter
```


- Open 3 tabs
```
watch -n 1 -t kubectl get hpa -n demo
```
```
watch -n 1 -t kubectl get pods -n demo
```
```
kubectl describe hpa http -n demo
```
> Warning  FailedGetPodsMetric           26s (x13 over 3m30s)  horizontal-pod-autoscaler  unable to get metric http_requests_per_second: unable to fetch metrics from custom metrics API: no custom metrics API (custom.metrics.k8s.io) registered  
```
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1 | jq
```
> Error from server (NotFound): the server could not find the requested resource  
- Deploy Prometheus adapter
> configmap last one
```
kubectl apply -f 6-prometheus-adapter
```
```
kubectl get apiservice
```

```
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1 | jq
```

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm search repo prometheus-adapter --max-col-width 23
```

```
helm install custom-metrics prometheus-community/prometheus-adapter \
--namespace monitoring \
 --version 2.14.2 \
--values 8-prometheus-adapter-helm/1-values.yaml
```

## Clean Up
```
helm repo remove prometheus-community
eksctl delete cluster -f eks.yaml
```