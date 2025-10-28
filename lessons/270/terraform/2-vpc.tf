# It's useful to manage public IP addresses outside of NAT/VPC module. 
# You can reuse them later or, for example, whitelist them with your customers for the webhook.
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${local.env}-nat"
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.4.0"

  name = local.env
  cidr = local.vpc_cidr

  azs             = [local.az1, local.az2]
  private_subnets = [local.private_subnet_az1_cidr, local.private_subnet_az2_cidr]
  public_subnets  = [local.public_subnet_az1_cidr, local.public_subnet_az2_cidr]

  enable_dns_hostnames   = true
  enable_dns_support     = true
  single_nat_gateway     = true
  enable_nat_gateway     = true
  reuse_nat_ips          = true
  one_nat_gateway_per_az = false
  external_nat_ip_ids    = [aws_eip.nat.id]

  map_public_ip_on_launch = true

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"                              = 1
    "kubernetes.io/cluster/${local.env}-${local.eks_cluster_name}" = "shared"
  }

  public_subnet_tags = {
    "kubernetes.io/role/elb"                                       = 1
    "kubernetes.io/cluster/${local.env}-${local.eks_cluster_name}" = "shared"
  }

  tags = {
    Env = local.env
  }
}
