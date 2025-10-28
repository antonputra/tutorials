resource "aws_route53_record" "postgres" {
  zone_id = aws_route53_zone.example_private.zone_id
  name    = "postgres.${aws_route53_zone.example_private.name}"
  type    = "A"
  ttl     = "300"
  records = [aws_instance.postgres.private_ip]
}
