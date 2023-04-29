variable "username" {
  description = "Username for the master user"
  type        = string
  sensitive   = true
}

variable "password" {
  description = "Password for the master user"
  type        = string
  sensitive   = true
}
