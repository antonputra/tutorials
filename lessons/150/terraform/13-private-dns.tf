locals {
  private_route53_zone  = "antonputra.pvt"
  arm64_private_ingress = "a756443acd77f4ef784dd5ab58a140fd-afe0a862b84f2ddf.elb.us-east-1.amazonaws.com"
  amd64_private_ingress = "aad023da206994f6bba16fdd00f5e51b-34f0df21e3edccc0.elb.us-east-1.amazonaws.com"
}

resource "aws_route53_zone" "private" {
  name = local.private_route53_zone

  vpc {
    vpc_id = aws_vpc.main.id
  }
}

resource "aws_route53_record" "api_arm64" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "api.arm64"
  type    = "CNAME"
  ttl     = 300
  records = [local.arm64_private_ingress]
}

resource "aws_route53_record" "api_amd64" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "api.amd64"
  type    = "CNAME"
  ttl     = 300
  records = [local.amd64_private_ingress]
}
