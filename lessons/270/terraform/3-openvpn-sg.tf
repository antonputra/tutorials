resource "aws_security_group" "openvpn" {
  name   = "${local.env}-openvpn"
  vpc_id = module.vpc.vpc_id

  tags = {
    Name = "${local.env}-openvpn"
  }
}

resource "aws_vpc_security_group_egress_rule" "openvpn_allow_all" {
  security_group_id = aws_security_group.openvpn.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"

  tags = {
    Name = "allow-all"
  }
}

resource "aws_vpc_security_group_ingress_rule" "openvpn_allow_ssh_from_anywhere" {
  security_group_id = aws_security_group.openvpn.id
  cidr_ipv4         = "0.0.0.0/0" # Potensially limit to corporate IPs.
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"

  tags = {
    Name = "allow-ssh-from-anywhere"
  }
}

resource "aws_vpc_security_group_ingress_rule" "openvpn_allow_1194_from_anywhere" {
  security_group_id = aws_security_group.openvpn.id
  cidr_ipv4         = "0.0.0.0/0" # Potensially limit to corporate IPs.
  from_port         = 1194
  to_port           = 1194
  ip_protocol       = "udp"

  tags = {
    Name = "allow-1194-from-anywhere"
  }
}
