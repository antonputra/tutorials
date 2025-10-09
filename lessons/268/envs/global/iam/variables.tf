variable "region" {
  type        = string
  description = "AWS region to provision infrastructure."
}

variable "bucket" {
  type        = string
  description = "S3 bucket for terraform state."
}

variable "github_repos" {
  type        = list(string)
  description = "GitHub repositories."
}
