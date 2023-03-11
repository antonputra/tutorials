resource "aws_security_group" "ec2_eg2" {
  name   = "ec2-eg2"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group" "alb_eg2" {
  name   = "alb-eg2"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group_rule" "ingress_ec2_eg2_traffic" {
  type                     = "ingress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ec2_eg2.id
  source_security_group_id = aws_security_group.alb_eg2.id
}

resource "aws_security_group_rule" "ingress_ec2_eg2_health_check" {
  type                     = "ingress"
  from_port                = 8081
  to_port                  = 8081
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ec2_eg2.id
  source_security_group_id = aws_security_group.alb_eg2.id
}

# resource "aws_security_group_rule" "full_egress_ec2_eg2" {
#   type              = "egress"
#   from_port         = 0
#   to_port           = 0
#   protocol          = "-1"
#   security_group_id = aws_security_group.ec2_eg2.id
#   cidr_blocks       = ["0.0.0.0/0"]
# }

resource "aws_security_group_rule" "ingress_alb_eg2_http_traffic" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  security_group_id = aws_security_group.alb_eg2.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "ingress_alb_eg2_https_traffic" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.alb_eg2.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "egress_alb_eg2_traffic" {
  type                     = "egress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  security_group_id        = aws_security_group.alb_eg2.id
  source_security_group_id = aws_security_group.ec2_eg2.id
}

resource "aws_security_group_rule" "egress_alb_eg2_health_check" {
  type                     = "egress"
  from_port                = 8081
  to_port                  = 8081
  protocol                 = "tcp"
  security_group_id        = aws_security_group.alb_eg2.id
  source_security_group_id = aws_security_group.ec2_eg2.id
}

resource "aws_launch_template" "my_app_eg2" {
  name                   = "my-app-eg2"
  image_id               = "ami-07309549f34230bcd"
  key_name               = "devops"
  vpc_security_group_ids = [aws_security_group.ec2_eg2.id]
}

resource "aws_lb_target_group" "my_app_eg2" {
  name     = "my-app-eg2"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    port                = 8081
    interval            = 30
    protocol            = "HTTP"
    path                = "/health"
    matcher             = "200"
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }
}

resource "aws_autoscaling_group" "my_app_eg2" {
  name     = "my-app-eg2"
  min_size = 1
  max_size = 3

  health_check_type = "EC2"

  vpc_zone_identifier = [
    aws_subnet.private_us_east_1a.id,
    aws_subnet.private_us_east_1b.id
  ]

  target_group_arns = [aws_lb_target_group.my_app_eg2.arn]

  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.my_app_eg2.id
      }
      override {
        instance_type = "t3.micro"
      }
    }
  }
}

resource "aws_autoscaling_policy" "my_app_eg2" {
  name                   = "my-app-eg2"
  policy_type            = "TargetTrackingScaling"
  autoscaling_group_name = aws_autoscaling_group.my_app_eg2.name

  estimated_instance_warmup = 300

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }

    target_value = 25.0
  }
}

resource "aws_lb" "my_app_eg2" {
  name               = "my-app-eg2"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_eg2.id]

  subnets = [
    aws_subnet.public_us_east_1a.id,
    aws_subnet.public_us_east_1b.id
  ]
}

resource "aws_lb_listener" "my_app_eg2" {
  load_balancer_arn = aws_lb.my_app_eg2.arn
  port              = "80"
  protocol          = "HTTP"

  # default_action {
  #   type             = "forward"
  #   target_group_arn = aws_lb_target_group.my_app_eg2.arn
  # }

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

data "aws_route53_zone" "public" {
  name         = "antonputra.com"
  private_zone = false
}

resource "aws_acm_certificate" "api" {
  domain_name       = "api.antonputra.com"
  validation_method = "DNS"
}

resource "aws_route53_record" "api_validation" {
  for_each = {
    for dvo in aws_acm_certificate.api.domain_validation_options : dvo.domain_name => {
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
  zone_id         = data.aws_route53_zone.public.zone_id
}

resource "aws_acm_certificate_validation" "api" {
  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [for record in aws_route53_record.api_validation : record.fqdn]
}

resource "aws_route53_record" "api" {
  name    = aws_acm_certificate.api.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.public.zone_id

  alias {
    name                   = aws_lb.my_app_eg2.dns_name
    zone_id                = aws_lb.my_app_eg2.zone_id
    evaluate_target_health = false
  }
}

resource "aws_lb_listener" "my_app_eg2_tls" {
  load_balancer_arn = aws_lb.my_app_eg2.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = aws_acm_certificate.api.arn
  ssl_policy        = "ELBSecurityPolicy-2016-08"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.my_app_eg2.arn
  }

  depends_on = [aws_acm_certificate_validation.api]
}

output "custom_domain" {
  value = "https://${aws_acm_certificate.api.domain_name}/ping"
}
