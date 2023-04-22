resource "aws_subnet" "us_east_1a" {
  vpc_id = aws_vpc.main.id

  cidr_block        = "10.0.0.0/19"
  availability_zone = "us-east-1a"
}

resource "aws_subnet" "us_east_1b" {
  vpc_id = aws_vpc.main.id

  cidr_block        = "10.0.32.0/19"
  availability_zone = "us-east-1b"
}
