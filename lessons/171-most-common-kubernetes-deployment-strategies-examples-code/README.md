# Most Common Kubernetes Deployment Strategies (Examples & Code)

You can find tutorial [here](https://youtu.be/lxc4EXZOOvE).

## Start Minikube

```bash
minikube start --driver=docker
```

## Deploy Prometheus (apply 2 times)

```bash
kubectl apply --server-side -R -f monitoring/
```

## Install Istio & Flagger

```bash
cd terraform
terraform apply
```

## Test application

```bash
kubectl run curl --image=alpine/curl:8.2.1 -n kube-system -i --tty --rm -- sh
for i in `seq 1 1000`; do curl myapp.default:8181/version; echo ""; sleep 1; done
```