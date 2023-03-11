resource "helm_release" "external_ingress_nginx" {
  name = "external"

  provider = helm.demo_arm64

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
    name  = "controller.replicaCount"
    value = "1"
  }

  # set {
  #   name  = "controller.nodeSelector.role"
  #   value = "ingress-nodes"
  # }

  # set {
  #   name  = "controller.tolerations[0].key"
  #   value = "service"
  # }

  # set {
  #   name  = "controller.tolerations[0].value"
  #   value = "ingress"
  # }

  # set {
  #   name  = "controller.tolerations[0].operator"
  #   value = "Equal"
  # }

  # set {
  #   name  = "controller.tolerations[0].effect"
  #   value = "NoExecute"
  # }
}


resource "helm_release" "external_ingress_nginx_amd64" {
  name = "external"

  provider = helm.demo_amd64

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
    name  = "controller.replicaCount"
    value = "1"
  }

  # set {
  #   name  = "controller.nodeSelector.role"
  #   value = "ingress-nodes"
  # }

  # set {
  #   name  = "controller.tolerations[0].key"
  #   value = "service"
  # }

  # set {
  #   name  = "controller.tolerations[0].value"
  #   value = "ingress"
  # }

  # set {
  #   name  = "controller.tolerations[0].operator"
  #   value = "Equal"
  # }

  # set {
  #   name  = "controller.tolerations[0].effect"
  #   value = "NoExecute"
  # }
}
