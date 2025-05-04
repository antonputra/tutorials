# FastAPI vs Node.js Performance Test on AWS EKS

This lesson compares the performance of FastAPI (Python) and Node.js applications running on AWS EKS. You can find the video tutorial [here](https://youtu.be/i3TcSeRO8gs).

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- kubectl
- helm
- Docker (for local testing)

## Directory Structure

```
lessons/236/
├── compose.yaml                 # Local development setup
├── deploy/
│   ├── node-app/               # Node.js K8s configs
│   └── python-app/             # FastAPI K8s configs
├── fastapi-app/                # Python application
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── postgres.yaml
│   └── memcached.yaml
├── migration/                  # Database schemas
├── node-app/                   # Node.js application
├── node-fastify-uws-app/      # Alternative Node.js impl
└── terraform/                  # AWS infrastructure
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

## Setup Instructions

1. **Deploy AWS Infrastructure**

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

2. **Configure kubectl**

```bash
aws eks update-kubeconfig --region us-west-2 --name performance-test-cluster
```

3. **Deploy Infrastructure Components**

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/memcached.yaml
```

4. **Deploy Applications**

```bash
# Deploy FastAPI application
kubectl apply -f deploy/python-app/

# Deploy Node.js application
kubectl apply -f deploy/node-app/
```

5. **Run Database Migrations**

```bash
# Port forward to PostgreSQL
kubectl port-forward svc/postgres -n performance-test 5432:5432

# Run migrations
cd migration
# Follow migration instructions in the migration directory
```

6. **Monitor Performance**

The monitoring stack should be set up using the configurations from lesson 135:
- Prometheus for metrics collection
- Grafana for visualization
- cAdvisor for container metrics

## Performance Testing

1. **Local Testing**
```bash
# Start local environment
docker compose up -d

# Run tests
# (Add your testing commands here)
```

2. **Kubernetes Testing**
```bash
# Get service endpoints
kubectl get svc -n performance-test

# Run performance tests
# (Add your testing commands here)
```

## Monitoring

Access Grafana dashboards for:
- CPU usage
- Memory consumption
- Network metrics
- Application-specific metrics

## Cleanup

```bash
# Delete Kubernetes resources
kubectl delete namespace performance-test

# Destroy AWS infrastructure
cd terraform
terraform destroy
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Node.js Documentation](https://nodejs.org/)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
