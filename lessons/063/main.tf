locals {
  vpc_id              = "vpc-08a51e4a8e1a4226b"
  private_a_subnet_id = "subnet-0e0317ff5d26c8b12"
  private_b_subnet_id = "subnet-0f4ec7d0ea60605bd"
  public_a_subnet_id  = "subnet-09316aa45c8669d28"
  public_b_subnet_id  = "subnet-08c7b53b2ca1d202b"

  ubuntu_ami = "ami-042e8287309f5df03"

  traffic_dist_map = {
    blue = {
      blue  = 100
      green = 0
    }
    blue-90 = {
      blue  = 90
      green = 10
    }
    split = {
      blue  = 50
      green = 50
    }
    green-90 = {
      blue  = 10
      green = 90
    }
    green = {
      blue  = 0
      green = 100
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Security Group
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web-servers with HTTP ports open within VPC"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

# Application Load Balancer
# At least two subnets in two different Availability Zones must be specified
# aws_lb: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb
resource "aws_lb" "app" {
  name               = "app-lb"
  internal           = false
  load_balancer_type = "application"
  subnets = [
    local.public_a_subnet_id,
    local.public_b_subnet_id
  ]
  security_groups = [aws_security_group.web.id]
}

# Load Balancer Listener
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_listener
resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "forward"
    # target_group_arn = aws_lb_target_group.blue.arn
    forward {
      target_group {
        arn    = aws_lb_target_group.blue.arn
        weight = lookup(local.traffic_dist_map[var.traffic_distribution], "blue", 100)
      }

      target_group {
        arn    = aws_lb_target_group.green.arn
        weight = lookup(local.traffic_dist_map[var.traffic_distribution], "green", 0)
      }

      stickiness {
        enabled  = false
        duration = 1
      }
    }
  }
}
