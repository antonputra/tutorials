resource "aws_subnet" "private" {
  vpc_id     = var.vpc_id
  cidr_block = var.cidr_block

  tags = {
    "Name" = "${var.env}-private"
  }
}
