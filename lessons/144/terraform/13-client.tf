resource "aws_instance" "client" {
  ami                    = data.aws_ami.ubuntu_jammy.id
  instance_type          = "t3a.xlarge"
  subnet_id              = aws_subnet.public_us_east_1a.id
  vpc_security_group_ids = [aws_security_group.client.id]

  iam_instance_profile = aws_iam_instance_profile.ssm_core.name

  tags = {
    Name = "client.antonputra.com"
  }
}

output "client" {
  value = aws_instance.client.id
}
