variable "vpcs" {
  description = "A list of VPCs."
  default     = ["main", "database", "client"]
}

output "vpcs" {
  value = "%{for vpc in var.vpcs}${vpc}, %{endfor}"
}

output "vpcs_index" {
  value = "%{for i, vpc in var.vpcs}(${i}) ${vpc}, %{endfor}"
}
