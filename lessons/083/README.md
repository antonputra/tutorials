# Cert Manager Kubernetes Tutorial (Let's Encrypt & Nginx Ingress & ACME | 5 Examples | YAML & HELM)

[YouTube Tutorial](https://youtu.be/7m4_kZOObzw)

## Prerequisites

- [Kubernetes](https://kubernetes.io/)
- [Helm 3](https://helm.sh/)

## Deploy Prometheus on Kubernetes
```bash
kubectl apply -f prometheus/0-crd
kubectl apply -f prometheus/1-prometheus-operator
kubectl apply -f prometheus/2-prometheus
kubectl get pods -n monitoring
```

## Deploy Cert Manager Helm & YAML

- Review default helm [values](https://github.com/jetstack/cert-manager/blob/master/deploy/charts/cert-manager/values.yaml)

- Add the Jetstack Helm repository

```bash
helm repo add jetstack \
    https://charts.jetstack.io
```

- Update your local Helm chart repository cache

```bash
helm repo update
```

- Create `cert-manager-values.yaml` file to override default variables

- Search for cert-manager

```bash
helm search repo cert-manager
```

- Generate YAML files

```bash
helm template cert-083 jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.5.3 \
  --values cert-manager-values.yaml \
  --output-dir helm-generated-yaml
```
- Create `cert-manager` namespace
```bash
kubectl apply -f cert-manager-ns.yaml
```

- Install cert-manager with Helm
```bash
helm install cert-083 jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.5.3 \
  --values cert-manager-values.yaml
```

- Get Helm releases
```bash
helm list -n cert-manager
```

- Get pods
```bash
kubectl get pods -n cert-manager
```
- [cert-manager](https://cert-manager.io/docs/concepts/)
- [cainjector](https://cert-manager.io/docs/concepts/ca-injector/)
- [webhook](https://cert-manager.io/docs/concepts/webhook/)

- Port forward Prometheus
```bash
kubectl port-forward svc/prometheus-operated 9090 -n monitoring
```

- Go to Prometheus targets `http://localhost:9090`

## Generate Self Signed Certificate (Example 1)
- Create SelfSigned ClusterIssuer `example-1/0-self-signed-issuer.yaml`

- Generate Self Signed Certificate `example-1/1-ca-certificate.yaml`
```bash
kubectl apply -f example-1
```

- Get certificate
```bash
kubectl get certificate -n cert-manager
```

- Get secrets
```bash
kubectl get secrets -n cert-manager
```

- Get x509 certificate
```bash
kubectl get secrets devopsbyexample-io-key-pair \
  -o yaml \
  -n cert-manager
```

- Decode base64 certificte
```bash
echo "base64" | base64 -d -o ca.crt
```

- Decode CA certificate
```bash
openssl x509 -in ca.crt -text -noout
```

## Generate TLS Certificate using CA (Example 2)
- Create CA ClusterIssuer `example-2/0-ca-issuer.yaml`

- Create `staging` namespace `example-2/1-staging-ns.yaml`

- Create certificate for blog.devopsbyexample.io `example-2/example-2/2-blog-certificate.yaml`
```bash
kubectl apply -f example-2
```

- Get certificate
```bash
kubectl get certificate -n staging
```

- Get secrets
```bash
kubectl get secrets -n staging
```

- Get x509 certificate
```bash
kubectl get secrets blog-devopsbyexample-io-key-pair \
  -o yaml \
  -n staging
```

- Decode base64 certificte
```bash
echo "base64" | base64 -d -o blog-devopsbyexample-io.crt
```

- Decode CA certificate
```bash
openssl x509 -in blog-devopsbyexample-io.crt -text -noout
```

## Deploy Nginx Ingress Controller
- Add ingress-nginx Helm repo
```bash
helm repo add ingress-nginx \
  https://kubernetes.github.io/ingress-nginx
```

- Update Helm repos
```bash
helm repo update
```

- Search for Nginx Helm Chart
```bash
helm search repo ingress-nginx
```

- Create `nginx-ingress-values.yaml` without ACME section

- Install Nginx Ingress
```bash
helm install ing-083 ingress-nginx/ingress-nginx \
  --namespace ingress \
  --version 4.0.1 \
  --values nginx-ingress-values.yaml \
  --create-namespace
```

- Get pods
```bash
kubectl get pods -n ingress
```

- Get Ingress Class
```bash
kubectl get ingressclass
```

## Deploy Grafana on Kubernetes

- Deploy Grafana using YAML
  - `grafana/0-secret.yaml`
  - `grafana/1-datasources.yaml`
  - `grafana/2-dashboard-providers.yaml`
  - `grafana/3-cert-manager.yaml`
  - `grafana/4-deployment.yaml`
  - `grafana/5-service.yaml`

```bash
kubectl apply -f grafana
```

- Get services in monitoring namespaces
```bash
kubectl get svc -n monitoring
```

- Create `HTTP` ingress without TLS section
  - `example-3/grafana.yaml`

```bash
kubectl apply -f example-3
```

- Get ingresses
```bash
kubectl get ing -n monitoring
```

- Create `CNAME` record for `grafana.devopsbyexample.io`

- Go to data sources and dashboards `http://grafana.devopsbyexample.io`

- Logout

- Install wireshark
```bash
brew install wireshark
```

- Get public ip address of Grafana
```bash
dig +short grafana.devopsbyexample.io
```

- Get network interfaces
```bash
ifconfig
```

- Get POST TCP packets
```bash
sudo tshark -i en1 -x -f "host grafana.devopsbyexample.io and port 80 and tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354" > post.pcap
```

```bash
cat post.pcap
```

- Add TLS section to grafana ingress
  - `example-3/grafana.yaml`

```bash
kubectl apply -f example-3
```

- Get certificates in monitoring namespace
```bash
kubectl get certificates -n monitoring
```

- Get ingresses in monitoring ns
```bash
kubectl get ing -n monitoring
```

- Go to `https://grafana.devopsbyexample.io` to check TLS certs

- Add CA to the keychain

- Login to Grafana

- Listen on port 443

```bash
sudo tshark -i en1 -x -f "port 443"
```

## Secure NGINX ingress with Let's Encrypt & ACME (Example 4)
- Create `letsencrypt-staging` Issuer in `monitoring` namespace
  - `example-4/letsencrypt-staging-issuer.yaml`

- Create `letsencrypt-staging` Issuer in `monitoring` namespace
  - `example-4/letsencrypt-prod-issuer.yaml`

```bash
kubectl apply -f example-4
```

- Get issuers in `monitoring` namespace
```bash
kubectl get issuers -n monitoring
```

- If it's not ready describe to get error message
```bash
kubectl describe issuer letsencrypt-http01-prod -n monitoring
```

- Create Prometheus ingress with `letsencrypt-prod` issuer
  - `example-4/2-prometheus-ing.yaml`


- Apply Prometheus ingress
```bash
kubectl apply -f example-4/2-prometheus-ing.yaml
```

- Get CRDs
```bash
kubectl get Certificates -n monitoring
kubectl describe Certificates \
  prometheus-v4-devopsbyexample-io-key-pair -n monitoring

kubectl get CertificateRequests -n monitoring
kubectl describe CertificateRequests \
  prometheus-v4-devopsbyexample-io-key-pair-ss2h8 -n monitoring

kubectl get Orders -n monitoring
kubectl describe Orders \
  prometheus-v4-devopsbyexample-io-key-pair-ss2h8-98152280 -n monitoring

kubectl get Challenges -n monitoring
kubectl describe Challenges \
  prometheus-v4-devopsbyexample-io-key-pair-2zjpw-9815-4236669664 -n monitoring
```

- Make sure that all pods are up in monitoring namespace including `cm-acme-http-solver-<id>`
```bash
kubectl get pods -n monitoring
```

- To complete we need to create CNAME record for prometheus
```bash
kubectl get ing -n monitoring
```

- Print out acme ing
```bash
kubectl get ing cm-acme-http-solver-lxtws -o yaml -n monitoring
```

- Watch Certificates and Challenges
```bash
watch -n 1 -t kubectl get certificates -n monitoring
watch -n 1 -t kubectl get Challenges -n monitoring
```

- Create CNAME for `prometheus-v4.devopsbyexample.io`

- Go to `https://prometheus-v4.devopsbyexample.io`

## Delegate a Subdomain to Route53
> [Creating a subdomain that uses Amazon Route 53 as the DNS service without migrating the parent domain](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingNewSubdomain.html)

- Create `monitoring.devopsbyexample.io` Route53 hosted zone

- Get Name Servers from `Hosted zone details`

- Add NS records for the subdomain `monitoring`

- Create A record to test route53 zone `test.monitoring.devopsbyexample.io` -> 10.10.10.10

- Wait up to 1 minute and test with dig

```bash
dig +short test.monitoring.devopsbyexample.io
```

## Create IAM Role for Kubernetes Service Account

- Create OpenID Connect provider, use `sts.amazonaws.com` for Audience

- Create IAM policy with Route53 access
  - `CertManagerRoute53Access`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "route53:GetChange",
      "Resource": "arn:aws:route53:::change/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets",
        "route53:ListResourceRecordSets"
      ],
      "Resource": "arn:aws:route53:::hostedzone/<id>"
    }
  ]
}
```

- Create IAM role for `cert-manager-acme` cert-manager

- Get service account name for cert-manager
```bash
kubectl get sa -n cert-manager
```

- Update trust for IAM role to allow only `cert-083-cert-manager` service account to assume it
```
aud -> sub
sts.amazonaws.com -> system:serviceaccount:cert-manager:cert-083-cert-manager
```

- Update service account manually, add following line to annotations
```bash
kubectl edit sa -n cert-manager
```
```yaml
eks.amazonaws.com/role-arn: arn:aws:iam::424432388155:role/cert-manager-acme
```

- Modify the cert-manager Deployment with the correct file system permissions, so the ServiceAccount token can be read.
```bash
kubectl get deployment -n cert-manager
kubectl edit deployment cert-083-cert-manager -n cert-manager
```
```yaml
- --issuer-ambient-credentials
```

- Make sure pod restarted
```bash
kubectl get pods -n cert-manager
```

- This change can be inclused to Helm Chart (include to `cert-manager-values.yaml` before installing or upgrade Helm release)
```yaml
serviceAccount:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::424432388155:role/cert-manager-acme
extraArgs: 
- --issuer-ambient-credentials
```

## Resolve DNS-01 challenge with cert-manager (Example 5)

- Create Issuer to use dns-01 challenge
  - `example-5/0-letsencrypt-staging-dns01-issuer.yaml`
  - `example-5/1-letsencrypt-prod-dns01-issuer.yaml`
  - `example-5/2-grafana-ing.yaml`

- Watch Certificates and Challenges
```bash
watch -n 1 -t kubectl get certificates -n monitoring
watch -n 1 -t kubectl get challenges -n monitoring
```

```bash
kubectl apply -f example-5
```

- Go to Route53 to get TXT record

- Create CNAME for grafana-v4.monitoring.devopsbyexample.io

- Go to `https://grafana-v4.monitoring.devopsbyexample.io`

- Check logs
```bash
kubectl get pods -n cert-manager
kubectl logs -f <pod> -n cert-manager
```

https://cert-manager.io/docs/configuration/acme/dns01/route53/

## Monitor Cert Manager with Prometheus and Grafana

## Clean Up
- Remove Helm repo
```bash
helm repo remove jetstack
helm repo remove ingress-nginx
```

- Remove wireshark
```bash
brew remove wireshark
```
- Remove `devopsbyexample.io` CA

- Delete Route53 hosted zone `monitoring.devopsbyexample.io`

- Delete all DNS records in google domains

- Delete IAM Role `cert-manager-acme`

- Delete IAM Policy `CertManagerRoute53Access`
