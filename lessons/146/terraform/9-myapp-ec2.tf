resource "aws_instance" "myapp" {
  ami           = data.aws_ami.ubuntu_jammy.id
  key_name      = "devops"
  instance_type = "t3a.large"
  subnet_id     = aws_subnet.public_us_east_1a.id

  vpc_security_group_ids = [
    aws_security_group.ssh.id,
    aws_security_group.myapp.id
  ]

  tags = {
    Name          = "myapp-000.antonputra.pvt"
    service       = "myapp"
    node-exporter = "true"
    rust-exporter = "true"
  }
}
