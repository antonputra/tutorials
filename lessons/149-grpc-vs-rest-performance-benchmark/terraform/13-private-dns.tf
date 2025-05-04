locals {
  private_route53_zone = "antonputra.pvt"
  private_ingress      = "a7f5d4a66fbd84473886cf25127341dc-4cebc8b4ce92c312.elb.us-east-1.amazonaws.com"
}

resource "aws_route53_zone" "private" {
  name = local.private_route53_zone

  vpc {
    vpc_id = aws_vpc.main.id
  }
}

resource "aws_route53_record" "rest" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "rest"
  type    = "CNAME"
  ttl     = 300
  records = [local.private_ingress]
}

resource "aws_route53_record" "grpc" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "grpc"
  type    = "CNAME"
  ttl     = 300
  records = [local.private_ingress]
}
