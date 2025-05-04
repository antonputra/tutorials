resource "helm_release" "flagger" {
  name = "flagger"

  repository       = "https://flagger.app"
  chart            = "flagger"
  namespace        = "flagger"
  create_namespace = true
  version          = "1.32.0"

  set {
    name  = "crd.create"
    value = "false"
  }

  set {
    name  = "meshProvider"
    value = "istio"
  }

  set {
    name  = "metricsServer"
    value = "http://prometheus-operated.monitoring:9090"
  }
}
