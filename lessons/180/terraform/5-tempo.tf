resource "helm_release" "tempo" {
  name = "tempo"

  repository       = "https://grafana.github.io/helm-charts"
  chart            = "tempo"
  namespace        = "monitoring"
  version          = "1.6.3"
  create_namespace = true

  values = [file("values/tempo.yaml")]
}
