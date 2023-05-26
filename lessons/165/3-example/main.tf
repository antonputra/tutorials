provider "aws" {
  region = "us-east-2"
}

resource "aws_instance" "example" {
  ami = "ami-0a695f0d95cefc163"

  instance_type = (
    terraform.workspace == "default" ? "t3.medium" : "t3.micro"
  )
}

terraform {
  backend "s3" {
    bucket         = "antonputra-terraform-state"
    key            = "workspaces-example/terraform.tfstate"
    dynamodb_table = "terraform-state"
    region         = "us-east-2"
    encrypt        = true
  }
}
