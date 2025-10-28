resource "helm_release" "grafana" {
  name = "grafana"

  repository       = "https://grafana.github.io/helm-charts"
  chart            = "grafana"
  namespace        = "monitoring"
  version          = "10.1.1"
  create_namespace = true

  values = [file("${path.module}/values/grafana.yaml")]

  depends_on = [helm_release.internal_nginx]
}
