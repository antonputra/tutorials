output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "AWS VPC id."
}

output "private_subet_ids" {
  value       = module.vpc.private_subnets
  description = "AWS private subnet IDs."
}

output "public_subet_ids" {
  value       = module.vpc.public_subnets
  description = "AWS private subnet IDs."
}
