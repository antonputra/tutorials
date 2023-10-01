# Crossplane Tutorial (vs Terraform): Create AWS VPC - EKS - IRSA - Cluster Autoscaler - CSI Driver

You can find tutorial [here](https://youtu.be/mpfqPXfX6mg).


## Install Crossplane on Kubernetes

```bash
minikube start --driver=docker
helm repo add crossplane-stable https://charts.crossplane.io/stable
helm repo update
helm search repo crossplane
helm install crossplane \
    --namespace crossplane-system \
    --create-namespace \
    --version 1.13.2 \
    crossplane-stable/crossplane

kubectl get pods -n crossplane-system
kubectl get crds | grep crossplane.io
```


## Create S3 Bucket using Crossplane

```bash
kubectl apply -f 0-crossplane/1-provider-aws-s3.yaml
kubectl get providers
kubectl get pods -n crossplane-system
kubectl get crds | grep aws.upbound.io
kubectl create secret generic aws-secret \
    -n crossplane-system \
    --from-file=creds=./aws-credentials.txt
kubectl apply -f 0-crossplane/0-provider-aws-config.yaml
kubectl apply -f 1-s3/0-my-bucket.yaml
kubectl get bucket
kubectl describe bucket
kubectl get bucket
kubectl apply -f 1-s3/1-my-bucket-versioning.yaml
kubectl get bucketversioning
```

## Create AWS VPC using Crossplane

```bash
kubectl apply -f 0-crossplane/2-provider-aws-ec2.yaml
kubectl get providers
kubectl apply -f 2-vpc
kubectl get VPC
kubectl get InternetGateway
kubectl get RouteTableAssociation
```

## Create EKS Cluster using Crossplane

```bash
kubectl apply -f 0-crossplane
kubectl get providers
kubectl apply -f 3-eks
kubectl get Cluster
kubectl get NodeGroup
aws configure --profile crossplane
aws eks update-kubeconfig --name dev-demo --region us-east-2 --profile crossplane
kubectl get nodes
```

## Create OpenID Connect Provider (OIDC)

```bash
kubectl apply -f 4-irsa
kubectl get OpenIDConnectProvider
kubectl get Addon
```

## Deploy EBS CSI driver

```bash
kubectl apply -f 5-storageclass
```

## Deploy Cluster Autoscaler

```bash
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm search repo cluster-autoscaler

helm install autoscaler \
    --namespace kube-system \
    --version 9.29.3 \
    --values 6-cluster-autoscaler/1-helm-values.yaml \
    autoscaler/cluster-autoscaler
```
