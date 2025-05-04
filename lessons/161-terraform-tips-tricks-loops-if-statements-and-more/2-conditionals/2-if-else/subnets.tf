variable "enable_public" {
  default = false
}

resource "aws_subnet" "public" {
  count = var.enable_public ? 1 : 0

  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.0.0/19"
}

resource "aws_subnet" "private" {
  count = var.enable_public ? 0 : 1

  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.0.0/19"
}

output "subnet_id" {
  value = (
    var.enable_public
    ? aws_subnet.public[0].id
    : aws_subnet.private[0].id
  )
}

output "subnet_id_v2" {
  value = one(concat(
    aws_subnet.public[*].id,
    aws_subnet.private[*].id
  ))
}
