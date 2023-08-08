resource "helm_release" "loadtester" {
  name = "loadtester"

  repository       = "https://flagger.app"
  chart            = "loadtester"
  namespace        = "istio-system"
  create_namespace = true
  version          = "0.28.1"

  depends_on = [helm_release.flagger]
}
