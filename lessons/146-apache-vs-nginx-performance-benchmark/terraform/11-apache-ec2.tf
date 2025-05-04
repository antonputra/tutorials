resource "aws_instance" "apache" {
  ami           = data.aws_ami.ubuntu_jammy.id
  key_name      = "devops"
  instance_type = "t3a.small"
  subnet_id     = aws_subnet.public_us_east_1a.id

  vpc_security_group_ids = [
    aws_security_group.ssh.id,
    aws_security_group.proxy.id
  ]

  tags = {
    Name          = "apache.antonputra.pvt"
    service       = "apache"
    node-exporter = "true"
  }
}
