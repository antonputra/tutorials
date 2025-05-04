variable "vpcs" {
  description = "A list of VPCs."
  default     = ["main", "database"]
}

output "new_vpcs" {
  value = [for vpc in var.vpcs : title(vpc)]
}

output "new_v2_vpc" {
  value = [for vpc in var.vpcs : title(vpc) if length(vpc) < 5]
}

variable "my_vpcs" {
  default = {
    main     = "main vpc"
    database = "vpc for database"
  }
}

output "my_vpcs" {
  value = [for name, desc in var.my_vpcs : "${name} is the ${desc}"]
}

output "my_vpcs_v2" {
  value = { for name, desc in var.my_vpcs : title(name) => title(desc) }
}
