# Install manually
# helm repo add grafana https://grafana.github.io/helm-charts
# helm repo update
# helm install grafana --namespace monitoring --create-namespace --version 6.60.6 --values terraform/values/grafana.yaml grafana/grafana
resource "helm_release" "grafana" {
  name = "grafana"

  repository       = "https://grafana.github.io/helm-charts"
  chart            = "grafana"
  namespace        = "monitoring"
  version          = "6.60.6"
  create_namespace = true

  values = [file("values/grafana.yaml")]
}
