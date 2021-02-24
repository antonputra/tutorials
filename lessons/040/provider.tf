provider "aws" {
  region  = "us-west-2"
  profile = "terraform"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
  backend "s3" {
    profile = "terraform"
    bucket = "antonputra-tfstate"
    key    = "services/server.tfstate"
    region = "us-west-2"
    dynamodb_table = "tfstate"
  }
}
