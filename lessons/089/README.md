# GitHub Actions Self Hosted Runner (Autoscaling with Kubernetes)

[YouTube Tutorial](https://youtu.be/lD0t-UgKfEo)

## Content

- Create GitHub Repository
- Create EKS Cluster with Terraform
- Install Cert-Manager on Kubernetes
- Install actions-runner-controller
- Create Single GitHub Actions Self Hosted Runner
- Create Multiple GitHub Actions Self Hosted Runners
- Autoscaling with Kubernetes

## Create GitHub Repository

- Create private GitHub repository `lesson-089`


## Create EKS Cluster with Terraform

- Go over each file under `terraform` folder

- Create EKS with terraform
```bash
terraform init
terraform apply
```

- Configure kubectl
```bash
aws eks --region us-east-1 update-kubeconfig --name demo
```
if you get an error `'NoneType' object is not iterable`, run `rm ~/.kube/config`

- Check connection with Kubernetes
```bash
kubectl get svc
```
## Install Cert-Manager on Kubernetes

- Add Helm repo
```bash
helm repo add jetstack https://charts.jetstack.io
```

- Update Helm
```bash
helm repo update
```

- Search for latest verion
```bash
helm search repo cert-manager
```

- Split the screen and install Helm chart
```bash
watch kubectl get pods -A
```

- Install Helm chart
```bash
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.6.0 \
  --set prometheus.enabled=false \
  --set installCRDs=true
```

## Install actions-runner-controller

- Create GitHub App, call it `k8s-actions-89`

- Create namespace
```bash
kubectl create ns actions
```

- Create secret to authenticate with GitHub
```bash
kubectl create secret generic controller-manager \
    -n actions \
    --from-literal=github_app_id=<> \
    --from-literal=github_app_installation_id=<> \
    --from-file=github_app_private_key=<>
```

- Add actions  helm repo
```bash
helm repo add actions-runner-controller https://actions-runner-controller.github.io/actions-runner-controller
helm repo update
helm search repo actions
```

- Install Helm chart
```bash
helm install actions \
    actions-runner-controller/actions-runner-controller \
    --namespace actions \
    --version 0.14.0 \
    --set syncPeriod=1m
```

## Create Single GitHub Actions Self Hosted Runner 

- Create `k8s/runner.yaml`
```bash
kubectl apply -f k8s/runner.yaml
kubectl get pods -n actions
kubectl logs -f k8s-single-runner -c runner -n actions
```

- Go to GitHub to check self hosted runners

- Clone `lesson-089` repository
```bash
git clone git@github.com:antonputra/lesson-089.git
```

- Create `.github/workflows/main.yaml`
- Commit & push
- Check pods
```bash
kubectl get pods -n actions
```

## Create Multiple GitHub Actions Self Hosted Runners

- Create `k8s/runner-deployment.yaml`
```bash
kubectl apply -f k8s/runner-deployment.yaml
kubectl get pods -n actions
```

- Check in GitHub repo self-hosted runners

- Create 2 build jobs with docker

- Create `Dockerfile`

- Ceate `.github/workflows/example-2.yaml`

## Autoscaling with Kubernetes

- Deploy `k8s/horizontal-runner-autoscaler.yaml`
```bash
kubectl apply -f k8s/horizontal-runner-autoscaler.yaml
```

- Ceate `.github/workflows/example-3.yaml`

## Links

- [Hosting your own runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [GitHub Actions Runner](https://github.com/actions/runner)
- [actions-runner-controller](https://github.com/actions-runner-controller/actions-runner-controller)
- [actions-runner-controller values.yaml](https://github.com/actions-runner-controller/actions-runner-controller/blob/master/charts/actions-runner-controller/values.yaml)
