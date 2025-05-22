resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "dev-nat"
  }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_zone1.id

  tags = {
    Name = "dev-nat"
  }

  depends_on = [aws_internet_gateway.igw]
}