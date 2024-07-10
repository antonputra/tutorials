resource "aws_vpc" "main" {
  cidr_block = var.cidr_block

  enable_dns_support   = false
  enable_dns_hostnames = false

  tags = {
    Name = "${var.env}-main"
  }
}
