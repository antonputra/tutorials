# Vertical Pod Autoscaling

[YouTube Tutorial](https://youtu.be/3h-vDDTZrm8)

## 1. Create EKS Cluster Using eksctl

- Create EKS cluster
```bash
eksctl create cluster -f eks.yaml
```
- Verify that you can connect to the cluster
```
kubectl get svc
```

## 2. Deploy Metrics server (YAML)

- List api services
```bash
kubectl get apiservice
```

- Use grep and filter by `metrics`
```bash
kubectl get apiservice | grep metrics
```

- Use kubectl to get metrics
```bash
kubectl top pods -n kube-system
```

- Access metrics API

```bash
kubectl get --raw /apis/metrics.k8s.io/v1beta1 | jq
```

- Create deployemnt files under `0-metrics-server` directory
  - `0-service-account.yaml`
  - `1-cluster-roles.yaml`
  - `2-role-binding.yaml`
  - `3-cluster-role-bindings.yaml`
  - `4-service.yaml`
  - `5-deployment.yaml`
  - `6-api-service.yaml`

- Apply created filies

```bash
kubectl apply -f 0-metrics-server
```

- Verify deployment

```bash
kubectl get pods -n kube-system
```

- List api services
```bash
kubectl get apiservice
```
- List services in `kube-system` namespace
```bash
kubectl get svc -n kube-system
```

- Access metrics API

```bash
kubectl get --raw /apis/metrics.k8s.io/v1beta1 | jq
```

- Get metrics for pods using raw command\
```bash
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods | jq
```

- Use kubectl to get metrics
```bash
kubectl top pods -n kube-system
```

## 3. Deploy Metrics server (HELM)

- Find default values for metrics-server [chart](https://github.com/bitnami/charts/tree/master/bitnami/metrics-server)
- Create `values.yaml` file
- Add `bitnami` helm repo
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
```

- Search for `metrics-server`
```bash
helm search repo metrics-server --max-col-width 23
```

- Install `metrics-server` Helm Chart
```bash
helm install metrics bitnami/metrics-server \
--namespace kube-system \
--version 5.8.13 \
--values values.yaml
```

## 3. Install Vertical Pod Autoscaler

- Open Autoscaler GitHub [page](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)

- Clone VPA repo
```bash
git clone https://github.com/kubernetes/autoscaler.git
```
- Change directory
```bash
cd autoscaler/vertical-pod-autoscaler
```
- Preview installation
```bash
./hack/vpa-process-yamls.sh print
```
- Install VPA
```bash
./hack/vpa-up.sh
```

- Tear down VPA
```bash
./hack/vpa-down.sh
```

## 4. Upgrade LibreSSL on Mac/OS X

- Get OpenSSL version
```bash
openssl version
```

- Upgrade LibreSSL with Homebew
```bash
brew install libressl
```

- Get OpenSSL version
```bash
openssl version
```
- Check instalation path of OpenSSL
```bash
which openssl
```
- Check version of the LibreSSL installed with Homebew
```bash
/opt/homebrew/opt/libressl/bin/openssl version
```
- Try to create a soft link
```bash
sudo ln -s /opt/homebrew/opt/libressl/bin/openssl /usr/bin/openssl
```
- Try to rename openssl
```bash
sudo mv /usr/bin/openssl /usr/bin/openssl-old
```

- Create soft link to /usr/local/bin/ which should take precedence on your path over /usr/bin.
```bash
sudo ln -s /opt/homebrew/opt/libressl/bin/openssl /usr/local/bin/openssl
```

- Open new tab and run version command
```bash
openssl version
```

## 5. Install Vertical Pod Autoscaler (Continue)

- Open new tab and change directory
```bash
cd Developer/autoscaler/vertical-pod-autoscaler
```

- Install VPA
```bash
./hack/vpa-up.sh
```

## 6. Demo
- Create deployment files under `1-demo` directory
 - `0-deployment.yaml`
 - `1-vpa.yaml`

- Open two tabs
```bash
watch -n 1 -t kubectl top pods
```

- Deploy sample app
```bash
kubectl apply -f 1-demo
```

- Let's run 5-10 min and in a new tab get VPA
```bash
kubectl get vpa
```

- Describe VPA
```bash
kubectl describe vpa hamster-vpa
```

- Update deployment and reapply
```bash
kubectl apply -f 1-demo/0-deployment.yaml
```

## Clean Up
- Delete EKS cluster
```
eksctl delete cluster -f eks.yaml
sudo rm /usr/local/bin/openssl
brew remove libressl
helm repo remove bitnami
rm -rf Developer/autoscaler
```
