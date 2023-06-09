data "aws_route53_zone" "public" {
  name         = "antonputra.com"
  private_zone = false
}

resource "aws_route53_record" "web" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = "service-a"
  type    = "CNAME"
  ttl     = 300
  records = ["k8s-ingress-external-0278203c2c-b04fe31f0de98ebe.elb.us-east-2.amazonaws.com"]
}
