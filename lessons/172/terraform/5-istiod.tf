resource "helm_release" "istiod" {
  name = "istiod"

  repository       = "https://istio-release.storage.googleapis.com/charts"
  chart            = "istiod"
  namespace        = "istio-system"
  create_namespace = true
  version          = "1.18.2"

  set {
    name  = "telemetry.enabled"
    value = "true"
  }

  depends_on = [helm_release.istio_base]
}
