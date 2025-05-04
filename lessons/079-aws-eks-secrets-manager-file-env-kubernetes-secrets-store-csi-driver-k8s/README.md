# AWS EKS & Secrets Manager (File & Env | Kubernetes | Secrets Store CSI Driver | K8s)

[YouTube Tutorial](https://youtu.be/Rmgo6vCytsg)

## 1. Create IAM User with Full Access
- Create `admin` user and place it in `Admin` IAM group
- Configure aws cli `aws configure`

## 2. Create Secret in AWS Secrets Manager
- Select `Other type of secrets`
- Create key: `MY_API_TOKEN` and random value: `7623fd72g3d`
- Give it a name `prod/service/token`
- Open created secret to check ARN

## 3. Create EKS Cluster Using eksctl
- Create `eks.yaml` config file
- Create EKS cluster
```bash
eksctl create cluster -f eks.yaml
```
- Check connection to EKS cluster
```bash
kubectl get svc
```

## 4. Create IAM OIDC Provider for EKS
- Copy `OpenID Connect provider URL`
- Create Identety Provider - select `OpenID Connect`
- Enter `sts.amazonaws.com` for Audience

## 5. Create IAM Policy to Read Secrets
- Create `APITokenReadAccess` IAM policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "<secret-arn>"
        }
    ]
}
```
## 6. Create IAM Role for a Kubernetes Service Account
- Click `Web identity` and select Identity provider that we created
- Select `APITokenReadAccess` IAM Policy
- Give it a name `api-token-access`
- Update trust relationships on the role 
- Update `aud` -> `sub`
- Update `sts.amazonaws.com` -> `system:serviceaccount:production:nginx`

## 7. Associate an IAM Role with Kubernetes Service Account
- Create `nginx/namespace.yaml`
- Create `nginx/service-account.yaml`
- Apply kubernetes objects
```bash
kubectl apply -f nginx
```
- Get Kubernetes namespaces
```bash
kubectl get ns
```
- Describe service account
```bash
kubectl get sa -n production
```

## 8. Install the Kubernetes Secrets Store CSI Driver
- Create `secrets-store-csi-driver/0-secretproviderclasses-crd.yaml`
- Create `secrets-store-csi-driver/1-secretproviderclasspodstatuses-crd.yaml`
- Apply CRDs
```bash
kubectl apply -f secrets-store-csi-driver
```
- Create `secrets-store-csi-driver/2-service-account.yaml`
- Create `secrets-store-csi-driver/3-cluster-role.yaml`
- Create `secrets-store-csi-driver/4-cluster-role-binding.yaml`
- Create `secrets-store-csi-driver/5-daemonset.yaml`
- Create `secrets-store-csi-driver/6-csi-driver.yaml`
- Apply Kubernetes objects
```bash
kubectl apply -f secrets-store-csi-driver
```
- Check the logs
```bash
kubectl logs -n kube-system -f -l app=secrets-store-csi-driver
```

- (Optionally) use helm chart
```bash
helm repo add secrets-store-csi-driver https://raw.githubusercontent.com/kubernetes-sigs/secrets-store-csi-driver/master/charts
```
- (Optionally) install helm chart
```bash
helm -n kube-system install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver
```

## 9. Install AWS Secrets & Configuration Provider (ASCP)
- Create `aws-provider-installer/0-service-account.yaml`
- Create `aws-provider-installer/1-cluster-role.yaml`
- Create `aws-provider-installer/2-cluster-role-binding.yaml`
- Create `aws-provider-installer/3-daemonset.yaml`
- Apply aws-provider-installer
```bash
kubectl apply -f aws-provider-installer
```
- Check logs
```bash
kubectl logs -n kube-system -f -l app=csi-secrets-store-provider-aws
```

## 10. Create Secret Provider Class
- Create `nginx/2-secret-provider-class.yaml`
```bash
kubectl apply -f nginx
```

## 11. Demo
- Create nginx `3-deployment.yaml`
- Open 2 tabs
```bash
kubectl logs -n kube-system -f -l app=secrets-store-csi-driver
```
```bash
kubectl apply -f nginx
```
```bash
kubectl -n production exec -it nginx-<id> -- bash
```
- Print mounted file
```bash
cat /mnt/api-token/secret-token
```
- Print environment variables with a secret
```bash
echo $API_TOKEN
```

## Bonus
[kubectx](https://github.com/ahmetb/kubectx)

## Clean Up
- Delete EKS Cluster
```bash
eksctl delete cluster -f eks.yaml
```
- Delete IAM Policy `APITokenReadAccess`
- Delete IAM Role `api-token-access`
- Delete IAM User `admin`

## Links
- [secrets-store-csi-driver](https://github.com/kubernetes-sigs/secrets-store-csi-driver)
- [AWS Secrets & Configuration Provider (ASCP)](https://github.com/aws/secrets-store-csi-driver-provider-aws)
- [Using Secrets Manager secrets in Amazon Elastic Kubernetes Service](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html)
- [How to use AWS Secrets & Configuration Provider with your Kubernetes Secrets Store CSI driver](https://aws.amazon.com/blogs/security/how-to-use-aws-secrets-configuration-provider-with-kubernetes-secrets-store-csi-driver/)
- [IAM role configuration](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts-technical-overview.html)
- [kubectx](https://github.com/ahmetb/kubectx)
