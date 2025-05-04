# Install Manually
# helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
# helm repo update
# helm install metrics-server --namespace kube-system --version 3.11.0 metrics-server/metrics-server --set "args[0]=--kubelet-insecure-tls"
resource "helm_release" "metrics_server" {
  name = "metrics-server"

  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = "3.11.0"

  set {
    name  = "args[0]"
    value = "--kubelet-insecure-tls"
  }
}
