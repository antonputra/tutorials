resource "aws_vpc_security_group_ingress_rule" "eks_allow_443_from_openvpn" {
  security_group_id            = aws_eks_cluster.eks.vpc_config[0].cluster_security_group_id
  referenced_security_group_id = aws_security_group.openvpn.id

  from_port   = 443
  to_port     = 443
  ip_protocol = "tcp"

  tags = {
    Name = "eks-allow-443-from-openvpn"
  }
}
