resource "aws_security_group" "my_server_ssh_access" {
  name        = "my-server-ssh-access"
  description = "Allow My Server SSH Accesss"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Allow SSH from Anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "ubuntu" {
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

resource "aws_instance" "my_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  key_name               = "old-key"
  subnet_id              = aws_subnet.public-us-east-1a.id
  vpc_security_group_ids = [aws_security_group.my_server_ssh_access.id]

  associate_public_ip_address = true

  tags = {
    Name = "My Server"
  }
}
