resource "aws_instance" "my-app-example-1" {
  ami           = "ami-0d5482f3cb962780f"
  instance_type = "t3.micro"
  key_name      = "devops"
  subnet_id     = aws_subnet.public-us-east-1a.id

  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.my-app-example-1.id]

  tags = {
    Name = "my-app-example-1"
  }
}
