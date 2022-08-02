resource "aws_apigatewayv2_domain_name" "api-v2" {
  domain_name = "api-v2.antonputra.com"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.api-v2.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  depends_on = [aws_acm_certificate_validation.api-v2]
}

resource "aws_route53_record" "api-v2" {
  name    = aws_apigatewayv2_domain_name.api-v2.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.public-example-3.zone_id

  alias {
    name                   = aws_apigatewayv2_domain_name.api-v2.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.api-v2.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_apigatewayv2_api_mapping" "api-v2" {
  api_id      = aws_apigatewayv2_api.api-gw-example-3.id
  domain_name = aws_apigatewayv2_domain_name.api-v2.id
  stage       = aws_apigatewayv2_stage.dev.id
}

output "custom_domain_api-v2" {
  value = "https://${aws_apigatewayv2_api_mapping.api-v2.domain_name}/health"
}
