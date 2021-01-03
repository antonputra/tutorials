# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance
# Resource: aws_instance

resource "aws_instance" "server" {
  ami           = var.ami
  instance_type = "t2.micro"

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [tags]
  }
}

resource "aws_eip" "ip" {
  vpc      = true
  instance = aws_instance.server.id
}
