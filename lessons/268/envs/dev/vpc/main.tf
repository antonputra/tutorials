# It's useful to manage public IP addresses outside of NAT/VPC module. 
# You can reuse them later or, for example, whitelist them with your customers for the webhook.
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = var.env
    Env  = var.env
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.4.0"

  name = var.env
  cidr = var.vpc_cidr

  azs             = [var.az1, var.az2]
  private_subnets = [var.private_subnet1_cidr, var.private_subnet2_cidr]
  public_subnets  = [var.public_subnet1_cidr, var.public_subnet2_cidr, ]

  enable_dns_hostnames   = true
  enable_dns_support     = true
  single_nat_gateway     = true
  enable_nat_gateway     = true
  reuse_nat_ips          = true
  one_nat_gateway_per_az = false
  external_nat_ip_ids    = [aws_eip.nat.id]

  map_public_ip_on_launch = true

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"                          = 1
    "kubernetes.io/cluster/${var.env}-${var.eks_cluster_name}" = "owned"
  }

  public_subnet_tags = {
    "kubernetes.io/role/elb"                                   = 1
    "kubernetes.io/cluster/${var.env}-${var.eks_cluster_name}" = "owned"
  }

  tags = {
    Env = var.env
  }
}
