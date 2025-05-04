resource "aws_db_subnet_group" "public" {
  name       = "public"
  subnet_ids = module.vpc.public_subnets
}
