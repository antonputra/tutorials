terraform {
  backend "s3" {
    bucket         = "antonputra-staging-terraform-state"
    key            = "workspaces-example/terraform.tfstate"
    dynamodb_table = "terraform-state"
    region         = "us-east-2"
    encrypt        = true
  }
}
