variable "subnet_cidr_blocks" {
  description = "CIDR blocks for the subnets."
  type        = list(string)
  default     = ["10.0.0.0/19", "10.0.32.0/19", "10.0.64.0/19"]
}

module "subnets" {
  source            = "../../modules/subnet"
  count             = length(var.subnet_cidr_blocks)
  vpc_id            = aws_vpc.main.id
  subnet_cidr_block = var.subnet_cidr_blocks[count.index]
}

output "all_ids" {
  value       = module.subnets[*].subnet_id
  description = "The IDs for all subnets."
}
