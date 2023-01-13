resource "helm_release" "external_ingress_nginx" {
  name = "external"

  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  version          = "4.4.2"

  set {
    name  = "controller.ingressClassResource.name"
    value = "external-ingress-nginx"
  }

  set {
    name  = "controller.metrics.enabled"
    value = "true"
  }

  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-type"
    value = "nlb"
  }

  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-internal"
    value = "false"
  }

  set {
    name  = "controller.podAnnotations.linkerd\\.io/inject"
    value = "enabled"
  }
}
