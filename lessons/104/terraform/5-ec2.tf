locals {
  # AWS key pair name
  # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
  key_name = "devops"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}

resource "aws_network_interface" "monitoring" {
  subnet_id       = aws_subnet.public-us-east-1a.id
  security_groups = [aws_security_group.monitoring.id]
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.small"

  key_name = local.key_name

  network_interface {
    network_interface_id = aws_network_interface.monitoring.id
    device_index         = 0
  }

  tags = {
    Name = "monitoring"
  }
}

output "ip" {
  value = aws_instance.web.public_ip
}
