provider "aws" {
  region = var.region
}

module "vpc" {
  source = "../../../modules/vpc"

  env        = "prod"
  cidr_block = "10.0.0.0/16"
}
