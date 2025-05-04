resource "aws_instance" "nginx" {
  ami           = "ami-0f35953afaa5c8c60"
  instance_type = "t3.micro"

  tags = {
    Name = "staging-nginx"
  }
}

resource "aws_instance" "nginx_2" {
  ami           = "ami-0f35953afaa5c8c60"
  instance_type = "t3.micro"

  tags = {
    Name = "staging-nginx"
  }
}
