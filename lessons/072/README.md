# How to Install Prometheus on Kubernetes Cluster?

[YouTube Tutorial](https://youtu.be/bwUECsVDbMA)

## Steps

### 0. Create EKS Cluster (Optional)
```bash
eksctl create cluster -f eks.yaml
```

### 1. Deploy Prometheus Stack Helm Chart
- Download `prometheus-values.yaml` file for **Prometheus** from [here](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- Update following variables

```yaml
etcd: false             # line 37
kubeScheduler: false    # line 53
adminPassword: test123  # line 628
kubeControllerManager:  # line 910
  enabled: false
kubeEtcd:               # line 1057
  enabled: false
kubeScheduler:          # line 1122
  enabled: false
serviceMonitorSelector: # line 2050
  matchLabels: 
    prometheus: devops
commonLabels:           # line 27
  prometheus: devops
```

```bash
helm repo add prometheus-community \
https://prometheus-community.github.io/helm-charts
```
```bash
helm repo update
```
```bash
helm search repo kube-prometheus-stack --max-col-width 23
```

```bash
helm install monitoring \
prometheus-community/kube-prometheus-stack \
--values prometheus-values.yaml \
--version 16.10.0 \
--namespace monitoring \
--create-namespace
```

```bash
kubectl get pods -n monitoring
```
```bash
kubectl get svc -n monitoring 
```
```bash
kubectl port-forward \
svc/monitoring-kube-prometheus-prometheus 9090 \
-n monitoring
```

- Go to `http://localhost:9090` and select `targets`

```bash
kubectl get cm kube-proxy-config -n kube-system -o yaml
```
```bash
kubectl -n kube-system get cm kube-proxy-config -o yaml |sed 's/metricsBindAddress: 127.0.0.1:10249/metricsBindAddress: 0.0.0.0:10249/' | kubectl apply -f -
```
```bash
watch -n 1 -t kubectl get pods -n kube-system
```
```bash
kubectl -n kube-system patch ds kube-proxy -p "{\"spec\":{\"template\":{\"metadata\":{\"labels\":{\"updateTime\":\"`date +'%s'`\"}}}}}"
```
- Go back to `http://localhost:9090` under `targets` and `alerts`

- Wait 20-30 min to get more data in Prometheus

```bash
kubectl port-forward \
svc/monitoring-grafana 3000:80 \
-n monitoring 
```

- Open following dashboards
  - Kubernetes / Compute Resources / Cluster
  - Kubernetes / Kubelet
  - USE Method / Cluster

### 2. Deploy Postgres Helm Chart

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
```
```bash
helm repo update
```
```bash
helm search repo postgresql --max-col-width 23
```

- Download `postgres-values.yaml` file for **Postgres** from [here](https://github.com/bitnami/charts/tree/master/bitnami/postgresql)


- Update following variables
```yaml
postgresqlDatabase: test  # line 155
metrics:                  # line 734
  enabled: true
serviceMonitor:           # line 744
  enabled: false
  additionalLabels:
    prometheus: devops
```

```bash
helm install postgres \
bitnami/postgresql \
--values postgres-values.yaml \
--version 10.5.0 \
--namespace db \
--create-namespace
```
```bash
kubectl get pods -n db
```

### 3. Create Service Monitor for Postgres
- Create `service-monitor.yaml`
```yaml
---
# https://github.com/prometheus-operator/prometheus-operator
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: postgres-postgresql
  namespace: db
  labels:
    <labels>
spec:
  endpoints:
  - port: <port>
    interval: 60s
    scrapeTimeout: 30s
  namespaceSelector:
    matchNames:
    - <namespace>
  selector:
    matchLabels:
      <labels>
```
```bash
kubectl get prometheus \
monitoring-kube-prometheus-prometheus \
-o yaml \
-n monitoring
```
```bash
kubectl get endpoints -n db
```

```bash
kubectl get services -n db
```

```bash
kubectl describe endpoints postgres-postgresql-metrics -n db
```

```bash
kubectl apply -f service-monitor.yaml
```

- Import Grafana dashboard `9628`

## Clean Up
```bash
helm repo remove prometheus-community bitnami
helm uninstall monitoring -n monitoring
helm uninstall postgres -n db
kubectl delete crd alertmanagerconfigs.monitoring.coreos.com
kubectl delete crd alertmanagers.monitoring.coreos.com
kubectl delete crd podmonitors.monitoring.coreos.com
kubectl delete crd probes.monitoring.coreos.com
kubectl delete crd prometheuses.monitoring.coreos.com
kubectl delete crd prometheusrules.monitoring.coreos.com
kubectl delete crd servicemonitors.monitoring.coreos.com
kubectl delete crd thanosrulers.monitoring.coreos.com
```
```bash
eksctl delete cluster -f eks.yaml
```
