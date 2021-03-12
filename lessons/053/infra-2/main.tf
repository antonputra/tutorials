provider "aws" {
  region = "us-east-1"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
  backend "s3" {
    bucket = "devopsbyexample-tf-state"
    key    = "platform.tfstate"
    region = "us-east-1"
  }
}

# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance
resource "aws_instance" "ubuntu" {
  ami           = "ami-013f17f36f8b1fefb"
  instance_type = "t3.micro"
  subnet_id     = "subnet-07fc2d0816e1f6100"
}
