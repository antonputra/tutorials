locals {
  env = "dev"

  region = "us-east-1"
  az1    = "us-east-1a"
  az2    = "us-east-1b"

  vpc_cidr = "10.0.0.0/16"

  private_subnet_az1_cidr = "10.0.0.0/19"
  private_subnet_az2_cidr = "10.0.32.0/19"
  public_subnet_az1_cidr  = "10.0.64.0/19"
  public_subnet_az2_cidr  = "10.0.96.0/19"

  eks_cluster_name = "main"
  eks_version      = "1.34"
}
