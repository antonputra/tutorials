# Kubernetes Canary Deployment (Manual vs Automated)

You can find tutorial [here](https://youtu.be/fWe6k4MmeSg).

## Start Minikube

```bash
minikube start --driver=docker
```

## Deploy All Dependencies

```bash
cd terraform
terraform apply
```

## Grafana

```bash
# username: admin, password: devops123
kubectl port-forward svc/grafana 3000 -n monitoring
```

## Test application (Example 1)

```bash
kubectl run curl --image=alpine/curl:8.2.1 -n default -i --tty --rm -- sh
for i in `seq 1 1000`; do curl myapp:8080/version; echo ""; sleep 1; done
```

## Test application (Example 2)

```bash
kubectl run curl --image=alpine/curl:8.2.1 -n staging -i --tty --rm -- sh
for i in `seq 1 1000`; do curl myapp:8080/version; echo ""; sleep 1; done
```
