resource "aws_instance" "nginx" {
  ami                    = data.aws_ami.ubuntu_jammy.id
  instance_type          = "t3a.small"
  subnet_id              = aws_subnet.public_us_east_1a.id
  vpc_security_group_ids = [aws_security_group.proxy.id]

  iam_instance_profile = aws_iam_instance_profile.ssm_core.name

  tags = {
    Name           = "nginx.antonputra.com"
    node-exporter  = "true"
    nginx-exporter = "true"
  }
}

output "nginx" {
  value = aws_instance.nginx.id
}
