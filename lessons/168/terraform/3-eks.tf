module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = var.eks_cluster_name
  cluster_version = "1.27"

  cluster_endpoint_public_access = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    nodes-amd64 = {
      desired_size = 2
      min_size     = 1
      max_size     = 2

      capacity_type  = "ON_DEMAND"
      instance_types = ["m6a.large"]
      ami_type       = "AL2_x86_64"
    }

    nodes-arm64 = {
      desired_size = 1
      min_size     = 1
      max_size     = 2

      capacity_type  = "ON_DEMAND"
      instance_types = ["m7g.large"]
      ami_type       = "AL2_ARM_64"
    }
  }
}
