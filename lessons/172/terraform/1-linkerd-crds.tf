resource "helm_release" "linkerd_crds" {
  name = "linkerd-crds"

  repository       = "https://helm.linkerd.io/stable"
  chart            = "linkerd-crds"
  namespace        = "linkerd"
  create_namespace = true
  version          = "1.6.1"
}
