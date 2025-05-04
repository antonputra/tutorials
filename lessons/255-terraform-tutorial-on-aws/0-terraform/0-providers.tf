provider "aws" {
  profile = "terraform-admin"
  region  = "us-east-2"
}

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.94"
    }
  }
}
