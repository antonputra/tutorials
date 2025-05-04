# Complete Setup Guide for AWS Beginners

This guide will walk you through setting up the performance test environment from scratch.

## 1. Initial Setup

### 1.1 Install Required Tools

**For Windows:**
```powershell
# Install AWS CLI
winget install -e --id Amazon.AWSCLI

# Install Terraform
winget install -e --id Hashicorp.Terraform

# Install kubectl
winget install -e --id Kubernetes.kubectl

# Install Helm
winget install -e --id Helm.Helm
```

**For macOS:**
```bash
# Install AWS CLI
brew install awscli

# Install Terraform
brew install terraform

# Install kubectl
brew install kubectl

# Install Helm
brew install helm
```

### 1.2 Configure AWS Account

1. Create an AWS Account if you don't have one:
   - Go to [AWS Console](https://aws.amazon.com)
   - Click "Create an AWS Account"
   - Follow the registration process

2. Create an IAM User:
   - Log in to AWS Console
   - Search for "IAM"
   - Click "Users" → "Add user"
   - Username: `eks-admin`
   - Select "Access key - Programmatic access"
   - Attach policies:
     - `AdministratorAccess` (for testing only, use more restricted policies in production)
   - Save the Access Key ID and Secret Access Key

3. Configure AWS CLI:
```bash
aws configure
# Enter the following when prompted:
AWS Access Key ID: [Your Access Key]
AWS Secret Access Key: [Your Secret Key]
Default region name: us-west-2
Default output format: json
```

4. Test AWS CLI configuration:
```bash
aws sts get-caller-identity
# Should show your account information
```

## 2. Deploy Infrastructure

### 2.1 Prepare Terraform Configuration

1. Create a new directory for your state file:
```bash
mkdir -p lessons/236/terraform/state
```

2. Initialize Terraform:
```bash
cd lessons/236/terraform
terraform init
```

### 2.2 Deploy AWS Resources

1. Review the planned changes:
```bash
terraform plan
```

2. Apply the configuration:
```bash
terraform apply
```
When prompted, type `yes` to confirm.

3. Save the outputs (you'll need these later):
```bash
terraform output > cluster-info.txt
```

## 3. Configure Kubernetes Access

1. Update kubeconfig with EKS cluster info:
```bash
aws eks update-kubeconfig --region us-west-2 --name performance-test-cluster
```

2. Verify cluster access:
```bash
kubectl get nodes
# Should show your EKS nodes
```

## 4. Deploy Applications

### 4.1 Create Namespace and Infrastructure

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Verify namespace creation
kubectl get namespaces | grep performance-test

# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Deploy Memcached
kubectl apply -f k8s/memcached.yaml

# Verify deployments
kubectl get pods -n performance-test
```

### 4.2 Deploy Applications

```bash
# Deploy FastAPI application
kubectl apply -f deploy/python-app/

# Deploy Node.js application
kubectl apply -f deploy/node-app/

# Verify all deployments
kubectl get all -n performance-test
```

## 5. Setup Monitoring

1. Add Helm repositories:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

2. Install Prometheus:
```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

3. Install Grafana dashboards:
```bash
kubectl apply -f lessons/135/monitoring/
```

## 6. Access Applications

1. Get service endpoints:
```bash
kubectl get svc -n performance-test
```

2. Port forward for local access:
```bash
# FastAPI application
kubectl port-forward svc/fastapi-service -n performance-test 8000:8000

# Node.js application
kubectl port-forward svc/nodejs-service -n performance-test 3000:3000

# Grafana dashboard
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
```

## 7. Run Performance Tests

### 7.1 Deploy Performance Testing Infrastructure

```bash
# Deploy the k6 test configuration and jobs
kubectl apply -f k8s/performance-test/k6-configmap.yaml
kubectl apply -f k8s/performance-test/k6-job.yaml
kubectl apply -f k8s/performance-test/k6-cronjob.yaml
```

### 7.2 Run Performance Tests

1. **Run a one-time test:**
```bash
# Start the k6 job
kubectl create job --from=cronjob/k6-load-test-periodic instant-test -n performance-test

# Monitor the test progress
kubectl logs -f job/instant-test -n performance-test

# Check test results
kubectl get job instant-test -n performance-test
```

2. **Monitor periodic tests:**
```bash
# Check CronJob status
kubectl get cronjobs -n performance-test

# List all test jobs
kubectl get jobs -n performance-test

# View results of the latest test
kubectl logs -l job-name=k6-load-test-periodic -n performance-test --tail=100
```

### 7.3 View Test Results in Grafana

1. Access the Grafana dashboard:
```bash
# Get Grafana admin password
kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 -d

# Port forward Grafana
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
```

2. Navigate to:
   - Dashboard → Browse
   - Look for "K6 Load Testing Results"
   - View detailed performance metrics

### 7.4 Customize Tests

1. Edit the test configuration:
```bash
# Edit the ConfigMap
kubectl edit configmap k6-test-script -n performance-test
```

2. Update test schedule:
```bash
# Edit the CronJob schedule
kubectl edit cronjob k6-load-test-periodic -n performance-test
```

## 8. Cleanup

When you're done testing, clean up to avoid unnecessary AWS charges:

1. Delete application resources:
```bash
kubectl delete namespace performance-test
kubectl delete namespace monitoring
```

2. Destroy AWS infrastructure:
```bash
cd terraform
terraform destroy
# Type 'yes' when prompted
```

3. Verify deletion:
```bash
aws eks list-clusters
# Should not show your cluster
```

## Common Issues and Solutions

1. **Error: Unable to access cluster**
   ```bash
   aws eks update-kubeconfig --region us-west-2 --name performance-test-cluster
   ```

2. **Error: Insufficient permissions**
   - Check IAM user permissions
   - Verify AWS CLI configuration

3. **Error: Pods not starting**
   ```bash
   kubectl describe pod [pod-name] -n performance-test
   ```

4. **Error: Cannot pull images**
   ```bash
   kubectl describe pod [pod-name] -n performance-test | grep "Failed"
   ```

## Estimated AWS Costs

- EKS Cluster: ~$0.10 per hour
- 2 x t3.medium nodes: ~$0.0416 per hour each
- NAT Gateway: ~$0.045 per hour
- Data transfer: Varies based on usage

Total estimated cost: ~$0.25-0.30 per hour ($180-220 per month)

## Additional Tips

1. Use AWS Cost Explorer to monitor expenses
2. Set up billing alerts in AWS
3. Always clean up resources after testing
4. Use AWS Free Tier services when possible
5. Consider spot instances for cost optimization 