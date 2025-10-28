# Find ubuntu ami
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/*ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}

# Allocate an Elastic IP
resource "aws_eip" "openvpn" {
  domain = "vpc"

  tags = {
    Name = "${local.env}-openvpn"
  }
}

# Create an EC2 instance
resource "aws_instance" "openvpn" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  key_name   = "aws" # TODO: use your own key
  monitoring = false
  subnet_id  = module.vpc.public_subnets[0]

  vpc_security_group_ids = [aws_security_group.openvpn.id]

  tags = {
    Name = "${local.env}-openvpn"
  }
}

# Associate the Elastic IP with the EC2 instance
resource "aws_eip_association" "openvpn" {
  instance_id   = aws_instance.openvpn.id
  allocation_id = aws_eip.openvpn.id
}
