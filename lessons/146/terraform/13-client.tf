resource "aws_instance" "client" {
  ami           = data.aws_ami.ubuntu_jammy.id
  key_name      = "devops"
  instance_type = "t3a.xlarge"
  subnet_id     = aws_subnet.public_us_east_1a.id

  vpc_security_group_ids = [
    aws_security_group.ssh.id,
    aws_security_group.client.id
  ]

  tags = {
    Name          = "client.antonputra.pvt"
    service       = "client"
    node-exporter = "true"
  }
}
