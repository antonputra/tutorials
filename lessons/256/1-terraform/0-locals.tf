locals {
  region   = "us-east-2"
  vpc_cidr = "10.0.0.0/16"
  env      = "dev"

  azs            = ["us-east-2a", "us-east-2b"]
  public_subnets = ["10.0.0.0/19", "10.0.32.0/19"]

  private_subnets = {

    public_1 = {
      cidr = cidrsubnet(local.vpc_cidr, 3, 2)
      az   = "us-east-2a"
    }

    public_2 = {
      cidr = cidrsubnet(local.vpc_cidr, 3, 3)
      az   = "us-east-2b"
    }

  }

  create_isolated_subnets = true

  ingress_rules = {
    22 = "63.10.10.10/32"
    80 = "0.0.0.0/0"
  }
}
