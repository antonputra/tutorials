# How Do I Get All the Pods on a NODE? (Filter Kubernetes Pods by Node NAME | Node LABEL)

## Create EKS Cluster
```bash
$ eksctl create cluster -f eks.yaml
```

## Delete EKS Cluster
```bash
$ eksctl delete cluster -f eks.yaml
```

## Deploy All Kuberentes Objects

```bash
kubectl apply -f k8s
```

## Build Docker Image

```bash
docker build -t express:v0.1.0 -f app/Dockerfile app
```

## Run Docker Image

```bash
docker run -p 8080:8080 express:v0.1.0
```

## Tag Docker Image

```bash
docker tag express:v0.1.0 424432388155.dkr.ecr.us-east-1.amazonaws.com/express:v0.1.0
```

## Push Docker Image to ECR

```bash
docker push 424432388155.dkr.ecr.us-east-1.amazonaws.com/express:v0.1.0
```

## Test Ingress

```bash
curl --resolve express.antonputra.com:80:54.83.73.161 http://express.antonputra.com/devops
```
