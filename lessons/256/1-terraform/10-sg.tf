resource "aws_security_group" "web" {
  name   = "web"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = local.ingress_rules

    content {
      from_port   = ingress.key
      to_port     = ingress.key
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

}
