resource "aws_acm_certificate" "api-v2" {
  domain_name       = "api-v2.antonputra.com"
  validation_method = "DNS"
}

data "aws_route53_zone" "public-example-3" {
  name         = "antonputra.com"
  private_zone = false
}

resource "aws_route53_record" "api-v2-validation-example-3" {
  for_each = {
    for dvo in aws_acm_certificate.api-v2.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.public-example-3.zone_id
}

resource "aws_acm_certificate_validation" "api-v2" {
  certificate_arn         = aws_acm_certificate.api-v2.arn
  validation_record_fqdns = [for record in aws_route53_record.api-v2-validation-example-3 : record.fqdn]
}
