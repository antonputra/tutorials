resource "aws_apigatewayv2_api" "api-gw-example-2" {
  name          = "api-gw-example-2"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "staging" {
  api_id = aws_apigatewayv2_api.api-gw-example-2.id

  name        = "staging"
  auto_deploy = true
}

resource "aws_apigatewayv2_vpc_link" "my-app-example-2" {
  name               = "my-app-example-2"
  security_group_ids = [aws_security_group.my-app-example-2.id]
  subnet_ids = [
    aws_subnet.private-us-east-1a.id,
    aws_subnet.private-us-east-1b.id
  ]
}

resource "aws_apigatewayv2_integration" "api-gw-example-2" {
  api_id = aws_apigatewayv2_api.api-gw-example-2.id

  integration_uri    = aws_lb_listener.my-app-example-2.arn
  integration_type   = "HTTP_PROXY"
  integration_method = "ANY"
  connection_type    = "VPC_LINK"
  connection_id      = aws_apigatewayv2_vpc_link.my-app-example-2.id
}

resource "aws_apigatewayv2_route" "api-gw-example-2" {
  api_id = aws_apigatewayv2_api.api-gw-example-2.id

  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api-gw-example-2.id}"
}
