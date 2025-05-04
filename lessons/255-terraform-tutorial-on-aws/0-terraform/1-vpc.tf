data "aws_vpc" "main" {
  id = "vpc-0f72e2035a414d7da"
}

output "vpc_cidr" {
  value = data.aws_vpc.main.cidr_block
}
