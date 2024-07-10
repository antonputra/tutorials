provider "aws" {
  region = var.region
}

module "subnet" {
  source = "../../../modules/subnet"

  vpc_id     = data.terraform_remote_state.vpc.outputs.vpc_id
  env        = "prod"
  cidr_block = "10.0.0.0/19"
}
