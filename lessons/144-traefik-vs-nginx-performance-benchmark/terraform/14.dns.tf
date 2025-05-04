# data "aws_route53_zone" "antonputra" {
#   name         = "antonputra.com."
#   private_zone = false
# }

resource "aws_route53_zone" "antonputra" {
  name = "antonputra.pvt"

  vpc {
    vpc_id = aws_vpc.main.id
  }
}

# HTTP private records
resource "aws_route53_record" "api_traefik" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "api.traefik"
  type    = "A"
  ttl     = 300
  records = [aws_instance.traefik.private_ip]
}

resource "aws_route53_record" "api_nginx" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "api.nginx"
  type    = "A"
  ttl     = 300
  records = [aws_instance.nginx.private_ip]
}

# gRPC private records
resource "aws_route53_record" "grpc_traefik" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "grpc.traefik"
  type    = "A"
  ttl     = 300
  records = [aws_instance.traefik.private_ip]
}

resource "aws_route53_record" "grpc_nginx" {
  zone_id = aws_route53_zone.antonputra.zone_id
  name    = "grpc.nginx"
  type    = "A"
  ttl     = 300
  records = [aws_instance.nginx.private_ip]
}
