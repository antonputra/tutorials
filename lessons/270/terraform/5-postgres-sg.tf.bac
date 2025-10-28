resource "aws_security_group" "postgres" {
  name   = "${local.env}-postgres"
  vpc_id = module.vpc.vpc_id

  tags = {
    Name = "${local.env}-postgres"
  }
}

resource "aws_vpc_security_group_egress_rule" "postgres_allow_all" {
  security_group_id = aws_security_group.postgres.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"

  tags = {
    Name = "allow-all"
  }
}

resource "aws_vpc_security_group_ingress_rule" "postgres_allow_ping_from_openvpn" {
  security_group_id            = aws_security_group.postgres.id
  referenced_security_group_id = aws_security_group.openvpn.id

  from_port   = 8
  to_port     = 0
  ip_protocol = "icmp"

  tags = {
    Name = "allow-ping-from-openvpn"
  }
}
