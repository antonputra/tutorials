provider "aws" {
  region = var.region
}

module "vpc" {
  source = "../../../modules/vpc-v2"

  env        = "dev"
  cidr_block = "10.0.0.0/16"
}
