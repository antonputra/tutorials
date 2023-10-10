# Azure Kubernetes Service (AKS) Tutorial: (Terraform - Nginx Ingress & TLS - OIDC Workload Identity)

You can find tutorial [here](https://youtu.be/8HmReos6dlY).

## Create AKS cluster using Terraform

```bash
az login
az account list
az account set --subscription <id>
terraform init
terraform apply
az aks get-credentials --resource-group tutorial --name dev-demo
```

## Create Public and Private load balancers

```bash
kubectl apply -f k8s/1-example
kubectl get svc
curl http://<ip>/
```

## Auto-Scaling

```bash
kubectl get nodes
kubectl apply -f k8s/2-example
kubectl get pods
kubectl describe pods nginx-v2-788b5579fd-dmbg8
kubectl get pods
kubectl get nodes
```

## Create an Ingress using Nginx Ingress

```bash
kubectl get svc -n ingress
kubectl apply -f k8s/3-example
kubectl get pods
kubectl get ing
curl --resolve "echo.antonputra.pvt:80:20.96.71.30" http://echo.antonputra.pvt/
```

## Secure the Ingress with TLS & Cert-manager

```bash
kubectl apply -f k8s/4-example
kubectl get pods
kubectl get ing
kubectl get Certificate
kubectl describe Certificate
kubectl describe CertificateRequest
kubectl describe Order
kubectl describe Challenge

kubectl get ing
kubectl get Certificate
dig echo.devopsbyexample.com
kubectl get ing
```

## Test Workload Identity

```bash
kubectl apply -f k8s/5-example
kubectl get pods -n dev
kubectl exec -it azure-cli-c97fd4f7c-rp2mc -n dev -- sh
az login --federated-token "$(cat $AZURE_FEDERATED_TOKEN_FILE)" --service-principal -u $AZURE_CLIENT_ID -t $AZURE_TENANT_ID
az storage blob list -c test --account-name devtest2392919
kubectl delete -f k8s/5-example
```
