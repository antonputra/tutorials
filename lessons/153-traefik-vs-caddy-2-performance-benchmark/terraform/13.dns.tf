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

resource "aws_route53_record" "api_caddy" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "api.caddy"
  type    = "A"
  ttl     = 300
  records = [aws_instance.caddy.private_ip]
}

resource "aws_route53_record" "api_traefik" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "api.traefik"
  type    = "A"
  ttl     = 300
  records = [aws_instance.traefik.private_ip]
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

resource "aws_route53_record" "api_traefik_public" {
  zone_id = data.aws_route53_zone.antonputra.zone_id
  name    = "api.traefik"
  type    = "A"
  ttl     = 300
  records = [aws_instance.traefik.public_ip]
}
