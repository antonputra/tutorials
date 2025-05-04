locals {
  public_route53_zone = "antonputra.com"
  public_ingress      = "ab3de63dd6b7040f0bebd66eaa3f5c00-760cbdf086108166.elb.us-east-1.amazonaws.com"
}

data "aws_route53_zone" "public" {
  name         = local.public_route53_zone
  private_zone = false
}

resource "aws_route53_record" "grafana" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "grafana"
  type    = "CNAME"
  ttl     = 300
  records = [local.public_ingress]
}

resource "aws_route53_record" "minio_console" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "minio-console"
  type    = "CNAME"
  ttl     = 300
  records = [local.public_ingress]
}

# Do NOT expose Prometheus to Internet (demo only)
resource "aws_route53_record" "prometheus" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "prometheus"
  type    = "CNAME"
  ttl     = 300
  records = [local.public_ingress]
}

# Do NOT expose Linerd Dashboard to Internet (demo only)
resource "aws_route53_record" "linerd" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "linerd"
  type    = "CNAME"
  ttl     = 300
  records = [local.public_ingress]
}
