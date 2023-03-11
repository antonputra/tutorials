locals {
  public_route53_zone = "antonputra.com"
  public_ingress      = "aac8baf90dcf0485287e1eb57909e9e0-41a8e9c5f0e45cba.elb.us-east-1.amazonaws.com"
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
