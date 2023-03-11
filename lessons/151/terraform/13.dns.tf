data "aws_route53_zone" "antonputra" {
  name         = "antonputra.com."
  private_zone = false
}

resource "aws_route53_zone" "antonputra" {
  name = "antonputra.pvt"

  vpc {
    vpc_id = aws_vpc.main.id
  }
}

# HTTP private records
resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "api"
  type    = "A"
  ttl     = 300
  records = [aws_instance.myapp.private_ip]
}

resource "aws_route53_record" "api_envoy" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "api.envoy"
  type    = "A"
  ttl     = 300
  records = [aws_instance.envoy.private_ip]
}

resource "aws_route53_record" "api_nginx" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "api.nginx"
  type    = "A"
  ttl     = 300
  records = [aws_instance.nginx.private_ip]
}

# HTTP public records
resource "aws_route53_record" "grafana" {
  zone_id = data.aws_route53_zone.antonputra.zone_id
  name    = "grafana"
  type    = "A"
  ttl     = 300
  records = [aws_instance.client.public_ip]
}

resource "aws_route53_record" "prometheus" {
  zone_id = data.aws_route53_zone.antonputra.zone_id
  name    = "prometheus"
  type    = "A"
  ttl     = 300
  records = [aws_instance.client.public_ip]
}
