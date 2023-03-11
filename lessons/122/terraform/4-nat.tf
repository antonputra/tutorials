# Allocate static public IP address to use it with NAT
resource "aws_eip" "nat" {
  vpc = true

  tags = {
    Name = "nat"
  }
}

# Create NAT Gateway to provide internet access for private subnets
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_us_east_1a.id

  tags = {
    Name = "nat"
  }

  depends_on = [aws_internet_gateway.igw]
}
