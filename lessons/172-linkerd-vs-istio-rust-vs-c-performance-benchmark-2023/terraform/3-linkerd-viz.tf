resource "helm_release" "linkerd_viz" {
  name = "linkerd-viz"

  repository       = "https://helm.linkerd.io/stable"
  chart            = "linkerd-viz"
  namespace        = "linkerd"
  create_namespace = true
  version          = "30.8.5"

  depends_on = [helm_release.linkerd_crds]
}
