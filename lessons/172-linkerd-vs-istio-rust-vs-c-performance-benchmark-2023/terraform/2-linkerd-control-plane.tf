resource "helm_release" "linkerd_control_plane" {
  name = "linkerd-control-plane"

  repository       = "https://helm.linkerd.io/stable"
  chart            = "linkerd-control-plane"
  namespace        = "linkerd"
  create_namespace = true
  version          = "1.12.5"

  set {
    name  = "identityTrustAnchorsPEM"
    value = file("linkerd/ca.crt")
  }

  set {
    name  = "identity.issuer.tls.crtPEM"
    value = file("linkerd/issuer.crt")
  }

  set {
    name  = "identity.issuer.tls.keyPEM"
    value = file("linkerd/issuer.key")
  }

  depends_on = [helm_release.linkerd_crds]
}
