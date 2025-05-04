module "vpcs" {
  source = "../../modules/vpc"

  enable_database_vpc = true
}
