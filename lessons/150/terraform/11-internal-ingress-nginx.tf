provider "helm" {
  alias = "demo_arm64"
  kubernetes {
    host                   = aws_eks_cluster.demo_arm64.endpoint
    cluster_ca_certificate = base64decode(aws_eks_cluster.demo_arm64.certificate_authority[0].data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      args        = ["eks", "get-token", "--cluster-name", aws_eks_cluster.demo_arm64.id]
      command     = "aws"
    }
  }
}

provider "helm" {
  alias = "demo_amd64"
  kubernetes {
    host                   = aws_eks_cluster.demo_amd64.endpoint
    cluster_ca_certificate = base64decode(aws_eks_cluster.demo_amd64.certificate_authority[0].data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      args        = ["eks", "get-token", "--cluster-name", aws_eks_cluster.demo_amd64.id]
      command     = "aws"
    }
  }
}

resource "helm_release" "internal_ingress_nginx" {
  name     = "internal"
  provider = helm.demo_arm64

  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  version          = "4.4.2"

  set {
    name  = "controller.ingressClassResource.name"
    value = "internal-ingress-nginx"
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
    value = "true"
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


resource "helm_release" "internal_ingress_nginx_amd64" {
  name     = "internal"
  provider = helm.demo_amd64

  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  version          = "4.4.2"

  set {
    name  = "controller.ingressClassResource.name"
    value = "internal-ingress-nginx"
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
    value = "true"
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
