# ArgoCD Notifications (Successful/Failed Deployments)

You can find tutorial [here](https://youtu.be/OP6IRsNiB4w).

## Commands from the Tutorial

```bash
minikube start
cd terraform
terraform init
terraform apply
kubectl get pods -n argocd
kubectl get svc -n argocd
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
kubectl port-forward svc/argocd-server 8080:80 -n argocd
git add .
git commit -m 'deploy nginx to staging'
git push origin main
kubectl apply -f k8s/
git add .
git commit -m 'fix the bug'
git push origin main
kubectl get application nginx -o yaml -n argocd
git add .
git commit -m 'update spec for nginx deployment'
git push origin main
```

```yaml
# nginx/deployment.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.0
          ports:
            - containerPort: 80
```
