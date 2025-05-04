# Go (Golang) vs Python Performance Benchmark (Kubernetes - OpenTelemetry - Prometheus - Grafana)

You can find tutorial [here](https://youtu.be/vJsqDqq1R0Y).

## Commands from the Tutorial

```bash
kubectl port-forward svc/tempo 4317 -n monitoring
kubectl port-forward svc/prometheus-operated 9090 -n monitoring
kubectl apply -R -f lessons/180/deployment
kubectl apply -f 1-test
kubectl apply -f 2-test
```