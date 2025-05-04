resource "aws_cloudwatch_log_group" "prometheus_demo" {
  name              = "/aws/prometheus/demo"
  retention_in_days = 14
}

resource "aws_prometheus_workspace" "demo" {
  alias = "demo"

  logging_configuration {
    log_group_arn = "${aws_cloudwatch_log_group.prometheus_demo.arn}:*"
  }
}
