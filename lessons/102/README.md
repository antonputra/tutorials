# How to Create EKS Cluster Using Terraform

[YouTube Tutorial](https://youtu.be/MZyrxzb7yAU)

## Create AWS VPC Using Terraform

- Create `terraform/0-provider.tf` terraform provider
- Create `terraform/1-vpc.tf` aws_vpc terraform resource

## Create Internet Gateway AWS Using Terraform

- Create `terraform/2-igw.tf` aws_internet_gateway terraform resource

## Create Private and Public Subnets in AWS Using Terraform

- Create `terraform/3-subnets.tf` 4 subnets using aws_subnet

## Create NAT Gateway in AWS Using Terraform

- Create `terraform/4-nat.tf` aws_eip and aws_nat_gateway
- Create `terraform/5-routes.tf` to associate routes with subnets

## Create EKS Cluster Using Terraform

- Create `terraform/6-eks.tf` EKS cluster

## Create IAM OIDC Provider EKS Using Terraform

- Create `terraform/8-iam-oidc.tf` IAM OIDC provider
- Create `terraform/9-iam-test.tf` to test AWS/K8s integration using service accounts
- Run `terraform apply`
- Copy `test_policy_arn`
- Export k8s config using `aws eks --region us-east-1 update-kubeconfig --name demo`
- Check if you can connect to K8s `kubectl get svc`
- Create `k8s/aws-test.yaml` without service account annotations - `kubectl apply -f k8s/aws-test.yaml`
- Get pods in default namespace `kubectl get pods`
- Check if you can list S3 buckets `kubectl exec aws-cli -- aws s3api list-buckets`
- Open `test-policy` role in AWS & Relationships
- Add annotation to service account and recreate pods 
```bash
kubectl delete -f k8s/aws-test.yaml
kubectl apply -f k8s/aws-test.yaml
```
- Try to list buckets again `kubectl exec aws-cli -- aws s3api list-buckets`

## Create Public Load Balancer on EKS

- Create `k8s/deployment.yaml` and `k8s/public-lb.yaml` and apply 
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/public-lb.yaml
kubectl get pods
kubectl get svc
```

- Find load balancer in AWS console by name. Verify that LB was created in public subnets

## Create Private Load Balancer on EKS

- Create `k8s/private-lb.yaml` and apply `kubectl apply -f k8s/private-lb.yaml`
- Get service `kubectl get svc`
- Find load balancer in AWS console by name. Verify that LB was created in private subnets

## Deploy EKS Cluster Autoscaler

- Create `terraform/10-iam-autoscaler.tf` and apply terraform `terraform apply`
- Create `k8s/cluster-autoscaler.yaml` and apply `kubectl apply -f k8s/cluster-autoscaler.yaml`
- Get pods `kubectl get pods -n kube-system`
- Check logs `kubectl logs -l app=cluster-autoscaler -n kube-system -f`

## EKS Cluster Auto Scaling Demo

- Verify that AG has required tags
  - k8s.io/cluster-autoscaler/<cluster-name> : owned
  - k8s.io/cluster-autoscaler/enabled : TRUE
- Split the scren `watch -n 1 -t kubectl get pods`
- Scale nginx from 1 to 5 and apply `kubectl apply -f k8s/deployment.yaml`
- Describe pod
- Run `watch -n 1 -t kubectl get nodes`
