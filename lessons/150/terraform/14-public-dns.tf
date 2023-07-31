locals {
  public_route53_zone = "antonputra.com"
}

data "aws_route53_zone" "public" {
  name         = local.public_route53_zone
  private_zone = false
}

# Do NOT expose Prometheus to Internet (demo only)
#arm64
data "kubernetes_service" "external-ingress-arm64" {
  provider = kubernetes.k8s-arm64
  metadata {
    name      = "external-ingress-nginx-controller"
    namespace = "ingress-nginx"
  }
  depends_on = [helm_release.external_ingress_nginx_arm64]
}
resource "aws_route53_record" "arm64_prometheus" {
  zone_id    = data.aws_route53_zone.public.zone_id
  name       = "prometheus.arm64"
  type       = "CNAME"
  ttl        = 300
  records    = [data.kubernetes_service.external-ingress-arm64.status.0.load_balancer.0.ingress.0.hostname]
  depends_on = [helm_release.external_ingress_nginx_arm64]
}

#amd64
data "kubernetes_service" "external-ingress-amd64" {
  provider = kubernetes.k8s-amd64
  metadata {
    name      = "external-ingress-nginx-controller"
    namespace = "ingress-nginx"
  }
  depends_on = [helm_release.external_ingress_nginx_amd64]
}
resource "aws_route53_record" "amd64_prometheus" {
  zone_id    = data.aws_route53_zone.public.zone_id
  name       = "prometheus.amd64"
  type       = "CNAME"
  ttl        = 300
  records    = [data.kubernetes_service.external-ingress-amd64.status.0.load_balancer.0.ingress.0.hostname]
  depends_on = [helm_release.external_ingress_nginx_amd64]
}
