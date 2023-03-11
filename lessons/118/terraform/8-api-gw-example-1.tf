resource "aws_apigatewayv2_api" "api-gw-example-1" {
  name          = "api-gw-example-1"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id = aws_apigatewayv2_api.api-gw-example-1.id

  name        = "prod"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "api-gw-example-1" {
  api_id = aws_apigatewayv2_api.api-gw-example-1.id

  integration_type   = "HTTP_PROXY"
  integration_uri    = "http://${aws_instance.my-app-example-1.public_ip}:8080/{proxy}"
  integration_method = "ANY"
  connection_type    = "INTERNET"
}

resource "aws_apigatewayv2_route" "api-gw-example-1" {
  api_id = aws_apigatewayv2_api.api-gw-example-1.id

  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api-gw-example-1.id}"
}

output "api_gw_example_1_health_url" {
  value = "${aws_apigatewayv2_stage.prod.invoke_url}/health"
}
