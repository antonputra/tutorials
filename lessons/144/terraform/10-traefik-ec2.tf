resource "aws_instance" "traefik" {
  ami                    = data.aws_ami.ubuntu_jammy.id
  instance_type          = "t3a.small"
  subnet_id              = aws_subnet.public_us_east_1a.id
  vpc_security_group_ids = [aws_security_group.proxy.id]

  iam_instance_profile = aws_iam_instance_profile.ssm_core.name

  tags = {
    Name             = "traefik.antonputra.com"
    node-exporter    = "true"
    traefik-exporter = "true"
  }
}

output "traefik" {
  value = aws_instance.traefik.id
}
