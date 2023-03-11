locals {
  public_route53_zone  = "antonputra.com"
  arm64_public_ingress = "a3857e85e94db4adf95bbcec0c282966-0022ac6243dac1c9.elb.us-east-1.amazonaws.com"
  amd64_public_ingress = "a1e60f2b9916a48648f5888cdaa97349-edf043af36c52334.elb.us-east-1.amazonaws.com"
}

data "aws_route53_zone" "public" {
  name         = local.public_route53_zone
  private_zone = false
}

# Do NOT expose Prometheus to Internet (demo only)
resource "aws_route53_record" "arm64_prometheus" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "prometheus.arm64"
  type    = "CNAME"
  ttl     = 300
  records = [local.arm64_public_ingress]
}

resource "aws_route53_record" "amd64_prometheus" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "prometheus.amd64"
  type    = "CNAME"
  ttl     = 300
  records = [local.amd64_public_ingress]
}
