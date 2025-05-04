locals {
  private_route53_zone = "antonputra.pvt"
  private_ingress      = "abe88f40829be42c5b3ad99a93fb7998-79f2b3e4c89e37f0.elb.us-east-1.amazonaws.com"
  private_rust         = "a842dda5a8e03460bbda4d98abcce46a-e8d8182e51984edd.elb.us-east-1.amazonaws.com"
  private_go           = "a2b2be55104d64d8da485a179c89fac6-ff69168b336c177f.elb.us-east-1.amazonaws.com"
}

resource "aws_route53_zone" "private" {
  name = local.private_route53_zone

  vpc {
    vpc_id = aws_vpc.main.id
  }
}

resource "aws_route53_record" "rust" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "api.rust"
  type    = "CNAME"
  ttl     = 300
  records = [local.private_ingress] # Terminate TLS by Ingress
  # records = [local.private_rust] # Terminate TLS by Rust itself
}

resource "aws_route53_record" "go" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "api.go"
  type    = "CNAME"
  ttl     = 300
  records = [local.private_ingress] # Terminate TLS by Ingress
  # records = [local.private_go] # Terminate TLS by Rust itself
}
