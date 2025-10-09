variable "env" {
  description = "Environment name."
}

variable "region" {
  description = "AWS region to provision infrastructure."
}

variable "eks_cluster_name" {
  description = "Name of the Amazon EKS cluster."
}

variable "eks_version" {
  description = "Amazon EKS cluster version."
}

variable "general_nodes_ec2_types" {
  description = "EC2 instance type for the general node group."
}

variable "general_nodes_count" {
  description = "Size of the general node group."
}

variable "terraform_s3_bucket" {
  type        = string
  description = "An S3 bucket to store the Terraform state."
}
