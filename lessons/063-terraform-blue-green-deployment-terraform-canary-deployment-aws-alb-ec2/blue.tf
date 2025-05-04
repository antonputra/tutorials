# EC2 Instance
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance
resource "aws_instance" "blue" {
  count = var.enable_blue_env ? var.blue_instance_count : 0

  ami                    = local.ubuntu_ami
  instance_type          = "t2.micro"
  subnet_id              = local.private_a_subnet_id
  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = templatefile("./init-script.sh", {
    file_content = "blue version 1.2 - ${count.index}"
  })

  tags = {
    Name = "blue version 1.2 - ${count.index}"
  }
}

# Load Balancer Target Group
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group
resource "aws_lb_target_group" "blue" {
  name     = "blue-tg-blue-lb"
  port     = 80
  protocol = "HTTP"
  vpc_id   = local.vpc_id

  health_check {
    port     = 80
    protocol = "HTTP"
    timeout  = 5
    interval = 10
  }
}

# Load Balancer Target Group Attachment
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group_attachment
resource "aws_lb_target_group_attachment" "blue" {
  count            = length(aws_instance.blue)
  target_group_arn = aws_lb_target_group.blue.arn
  target_id        = aws_instance.blue[count.index].id
  port             = 80
}