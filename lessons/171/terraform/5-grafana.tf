resource "helm_release" "grafana" {
  name = "grafana"

  repository       = "https://flagger.app"
  chart            = "grafana"
  namespace        = "istio-system"
  create_namespace = true
  version          = "1.7.0"

  set {
    name  = "url"
    value = "http://prometheus-operated.monitoring:9090"
  }

  depends_on = [helm_release.flagger]
}
