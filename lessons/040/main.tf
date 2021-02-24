# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance
# Resource: aws_instance

resource "aws_instance" "server" {
  # The AMI to use for the instance.
  ami = var.ami

  # The type of instance to start.
  instance_type = "t2.micro"

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [tags]
  }
}

# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eip
# Resource: aws_eip

resource "aws_eip" "ip" {
  vpc      = true
  instance = aws_instance.server.id
}
