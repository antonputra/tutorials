locals {
  private_route53_zone = "antonputra.pvt"
}

resource "aws_route53_zone" "private" {
  name = local.private_route53_zone

  vpc {
    vpc_id = aws_vpc.main.id
  }
}

#arm64
provider "kubernetes" {
  alias                  = "k8s-arm64"
  host                   = aws_eks_cluster.demo_arm64.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.demo_arm64.certificate_authority[0].data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", aws_eks_cluster.demo_arm64.id]
    command     = "aws"
  }
}

data "kubernetes_service" "internal-ingress-arm64" {
  provider = kubernetes.k8s-arm64
  metadata {
    name      = "internal-ingress-nginx-controller"
    namespace = "ingress-nginx"
  }
  depends_on = [helm_release.internal_ingress_nginx_arm64]
}

resource "aws_route53_record" "api_arm64" {
  zone_id    = aws_route53_zone.private.zone_id
  name       = "api.arm64"
  type       = "CNAME"
  ttl        = 300
  records    = [data.kubernetes_service.internal-ingress-arm64.status.0.load_balancer.0.ingress.0.hostname]
  depends_on = [helm_release.internal_ingress_nginx_arm64]
}

#amd64
provider "kubernetes" {
  alias                  = "k8s-amd64"
  host                   = aws_eks_cluster.demo_amd64.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.demo_amd64.certificate_authority[0].data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", aws_eks_cluster.demo_amd64.id]
    command     = "aws"
  }
}

data "kubernetes_service" "internal-ingress-amd64" {
  provider = kubernetes.k8s-amd64
  metadata {
    name      = "internal-ingress-nginx-controller"
    namespace = "ingress-nginx"
  }
  depends_on = [helm_release.internal_ingress_nginx_amd64]
}

resource "aws_route53_record" "api_amd64" {
  zone_id    = aws_route53_zone.private.zone_id
  name       = "api.amd64"
  type       = "CNAME"
  ttl        = 300
  records    = [data.kubernetes_service.internal-ingress-amd64.status.0.load_balancer.0.ingress.0.hostname]
  depends_on = [helm_release.internal_ingress_nginx_amd64]
}
