# Build a Secure AWS EKS CI/CD Pipeline: Step-by-Step Tutorial (ArgoCD + GitHub Actions)

You can find tutorial [here](https://youtu.be/KOE_6QYQqA4).

## Commands

```bash
cd envs/global/s3
terraform init
terraform apply -var-file=../global.tfvars
terraform init -migrate-state -backend-config=../state.config
cd ../iam
terraform init -backend-config=../state.config
terraform apply -var-file=../global.tfvars
cd ../ecr
terraform init -backend-config=../state.config
terraform apply -var-file=../global.tfvars
git commit --allow-empty -m "trigger ci/cd"
git push origin main
cd ../../dev/vpc/
terraform init -backend-config=../state.config
terraform apply -var-file=../dev.tfvars -var-file=vpc.tfvars
cd ../eks
terraform init -backend-config=../state.config
terraform apply -var-file=../dev.tfvars -var-file=eks.tfvars
aws eks update-kubeconfig --name dev-main --region us-east-1
kubectl get pods -A
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
kubectl port-forward svc/argocd-server 8080:80 -n argocd
ssh-keygen -t ed25519 -C "aputra@antonputra.com" -f ~/.ssh/argocd_ed25519
cd ../../..
kubectl apply -f k8s/repo-secret.yaml
kubectl apply -f k8s/application.yaml
kubectl get pods -n my-app
kubectl get pods -n my-app -o wide
dig k8s-myapp-myapp-a6d50e5e0c-2ce465b175ee5624.elb.us-east-1.amazonaws.com
curl -i http://k8s-myapp-myapp-b6d0d28cfe-57e6e2d80218d4d4.elb.us-east-1.amazonaws.com:8080/version
kubectl get pods -n my-app
for i in `seq 1 100000`; do curl -m 10 http://k8s-myapp-myapp-b6d0d28cfe-57e6e2d80218d4d4.elb.us-east-1.amazonaws.com:8080/version; sleep 1; done
git commit --allow-empty -m "trigger ci/cd"
git push origin main
kubectl get pods -n argocd
kubectl logs -f argocd-application-controller-0 -n argocd
```
