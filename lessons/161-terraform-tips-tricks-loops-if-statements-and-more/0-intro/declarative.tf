resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "staging-main"
  }
}

resource "aws_instance" "nginx" {
  ami           = "ami-0f35953afaa5c8c60"
  instance_type = "t3.micro"

  tags = {
    Name = "staging-nginx"
  }
}
