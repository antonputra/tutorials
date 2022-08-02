resource "aws_lb_target_group" "my-app-example-3" {
  name     = "my-app-example-3"
  port     = 8080
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled  = true
    protocol = "TCP"
  }
}

resource "aws_lb" "my-app-example-3" {
  name               = "my-app-example-3"
  internal           = true
  load_balancer_type = "network"

  subnets = [
    aws_subnet.private-us-east-1a.id,
    aws_subnet.private-us-east-1b.id
  ]
}

resource "aws_lb_listener" "my-app-example-3" {
  load_balancer_arn = aws_lb.my-app-example-3.arn
  port              = "8080"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.my-app-example-3.arn
  }
}
