locals {
  public_route53_zone = "antonputra.com"
  public_ingress      = "a717644449be440aab8c800d5ba6ef4c-973e91bc4940dee1.elb.us-east-1.amazonaws.com"
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

# Do NOT expose Prometheus to Internet (demo only)
resource "aws_route53_record" "prometheus" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "prometheus"
  type    = "CNAME"
  ttl     = 300
  records = [local.public_ingress]
}
