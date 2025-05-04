# OpenTelemetry Golang Tutorial (Tracing in Grafana & Kubernetes & Tempo)

You can find tutorial [here](https://youtu.be/ZIN7H00ulQw).

## Commands from the Tutorial

```bash
git clone git@github.com:antonputra/tutorials.git
cd tutorials/lessons/178
cd terraform
terraform init
terraform apply
cd ..
cd myapp
go mod tidy
kubectl get pods -n monitoring
kubectl port-forward svc/tempo 4318 -n monitoring
export OTLP_ENDPOINT=localhost:4318
curl http://0.0.0.0:8080/devices
kubectl port-forward svc/grafana 3000:80 -n monitoring
# Datasource URL: http://tempo.monitoring:3100
kubectl apply -f k8s
kubectl get pods -n default
kubectl get svc -n default
kubectl port-forward svc/myapp 8080:8080 -n default
```
