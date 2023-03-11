resource "aws_lb_target_group" "my-app-example-2" {
  name     = "my-app-example-2"
  port     = 8080
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled  = true
    protocol = "HTTP"
    path     = "/health"
  }
}

resource "aws_lb_target_group_attachment" "my-app-example-2" {
  target_group_arn = aws_lb_target_group.my-app-example-2.arn
  target_id        = aws_instance.my-app-example-2.id
  port             = 8080
}

resource "aws_lb" "my-app-example-2" {
  name               = "my-app-example-2"
  internal           = true
  load_balancer_type = "network"

  subnets = [
    aws_subnet.private-us-east-1a.id,
    aws_subnet.private-us-east-1b.id
  ]
}

resource "aws_lb_listener" "my-app-example-2" {
  load_balancer_arn = aws_lb.my-app-example-2.arn
  port              = "8080"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.my-app-example-2.arn
  }
}
