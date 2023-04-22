resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "main"
  }
}

resource "aws_vpc" "database" {
  count = var.enable_database_vpc ? 1 : 0

  cidr_block = "10.1.0.0/16"

  tags = {
    Name = "database"
  }
}
