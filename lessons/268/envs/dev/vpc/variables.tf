variable "env" {
  description = "Environment name."
}

variable "region" {
  description = "AWS region to provision infrastructure."
}

variable "vpc_cidr" {
  description = "CIDR range for the AWS virtual private cloud."
}

variable "az1" {
  description = "Availability zone in AWS."
}

variable "az2" {
  description = "Availability zone in AWS."
}

variable "private_subnet1_cidr" {
  description = "CIDR range for the private subnet."
}

variable "private_subnet2_cidr" {
  description = "CIDR range for the private subnet."
}

variable "public_subnet1_cidr" {
  description = "CIDR range for the public subnet."
}

variable "public_subnet2_cidr" {
  description = "CIDR range for the public subnet."
}

variable "eks_cluster_name" {
  description = "Name of the Amazon EKS cluster."
}

variable "terraform_s3_bucket" {
  type        = string
  description = "An S3 bucket to store the Terraform state."
}
