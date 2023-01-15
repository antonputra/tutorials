# HTTP private records
resource "aws_route53_zone" "antonputra_pvt" {
  name = "antonputra.pvt"

  vpc {
    vpc_id = aws_vpc.main.id
  }
}

resource "aws_route53_record" "myapp" {
  zone_id = aws_route53_zone.antonputra_pvt.zone_id
  name    = "myapp-000"
  type    = "A"
  ttl     = 300
  records = [aws_instance.myapp.private_ip]
}

resource "aws_route53_record" "nginx" {
  zone_id = aws_route53_zone.antonputra_pvt.zone_id
  name    = "api.nginx"
  type    = "A"
  ttl     = 300
  records = [aws_instance.nginx.private_ip]
}

resource "aws_route53_record" "apache" {
  zone_id = aws_route53_zone.antonputra_pvt.zone_id
  name    = "api.apache"
  type    = "A"
  ttl     = 300
  records = [aws_instance.apache.private_ip]
}

# HTTP public records
data "aws_route53_zone" "antonputra_com" {
  name         = "antonputra.com."
  private_zone = false
}

resource "aws_route53_record" "monitoring" {
  zone_id = data.aws_route53_zone.antonputra_com.zone_id
  name    = "monitoring"
  type    = "A"
  ttl     = 300
  records = [aws_instance.monitoring.public_ip]
}
