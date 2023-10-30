resource "helm_release" "prometheus_operator_crds" {
  name = "prometheus-operator-crds"

  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "prometheus-operator-crds"
  namespace        = "monitoring"
  create_namespace = true
  version          = "6.0.0"
}
