resource "aws_route53_zone" "example_private" {
  name = "example.pvt"
  vpc {
    vpc_id = module.vpc.vpc_id
  }
}
