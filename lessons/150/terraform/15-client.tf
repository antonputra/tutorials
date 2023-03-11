data "aws_ami" "ubuntu_jammy" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}

resource "aws_security_group" "client" {
  name   = "client"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "Allow SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow ALL outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "client" {
  ami           = data.aws_ami.ubuntu_jammy.id
  key_name      = "devops"
  instance_type = "t3a.xlarge"
  subnet_id     = aws_subnet.public_us_east_1a.id

  vpc_security_group_ids = [
    aws_security_group.client.id
  ]

  tags = {
    Name          = "client.antonputra.pvt"
    service       = "client"
    node-exporter = "true"
  }
}
