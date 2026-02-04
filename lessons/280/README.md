# Kubernetes Networking: NodePort, LoadBalancer, Ingress, or Gateway API?

You can find tutorial [here](https://youtu.be/sjaOsHoF6KY).

## Commands:

```bash
helm upgrade --install ingress ingress-nginx/ingress-nginx --values values/nginx-ingress.yaml --namespace ingress --create-namespace
kubectl get ingressclass
kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/standard-install.yaml
helm upgrade --install istiod istio/istiod --namespace istio-system --create-namespace
kubectl get gatewayclass
```
