resource "aws_network_interface" "myapp" {
  subnet_id       = aws_subnet.private_us_east_1a.id
  security_groups = [aws_security_group.myapp.id]
  private_ips     = ["10.0.32.200"]

  tags = {
    Name = "myapp.antonputra.pvt"
  }
}

resource "aws_instance" "myapp" {
  ami                  = data.aws_ami.ubuntu_jammy.id
  instance_type        = "t3a.large"
  iam_instance_profile = aws_iam_instance_profile.ssm_core.name

  network_interface {
    network_interface_id = aws_network_interface.myapp.id
    device_index         = 0
  }

  tags = {
    Name          = "myapp.antonputra.pvt"
    node-exporter = "true"
  }
}

output "myapp" {
  value = aws_instance.myapp.id
}
