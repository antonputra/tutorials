resource "aws_apigatewayv2_api" "api-gw-example-3" {
  name          = "api-gw-example-3"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "dev" {
  api_id = aws_apigatewayv2_api.api-gw-example-3.id

  name        = "dev"
  auto_deploy = true
}

resource "aws_apigatewayv2_vpc_link" "my-app-example-3" {
  name               = "my-app-example-3"
  security_group_ids = [aws_security_group.my-app-example-3.id]
  subnet_ids = [
    aws_subnet.private-us-east-1a.id,
    aws_subnet.private-us-east-1b.id
  ]
}

resource "aws_apigatewayv2_integration" "api-gw-example-3" {
  api_id = aws_apigatewayv2_api.api-gw-example-3.id

  integration_uri    = aws_lb_listener.my-app-example-3.arn
  integration_type   = "HTTP_PROXY"
  integration_method = "ANY"
  connection_type    = "VPC_LINK"
  connection_id      = aws_apigatewayv2_vpc_link.my-app-example-3.id
}

resource "aws_apigatewayv2_route" "api-gw-example-3" {
  api_id = aws_apigatewayv2_api.api-gw-example-3.id

  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api-gw-example-3.id}"
}
