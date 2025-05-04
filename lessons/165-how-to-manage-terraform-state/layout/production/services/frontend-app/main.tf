terraform {
  backend "s3" {
    bucket         = "antonputra-production-terraform-state"
    key            = "services/frontend-app/terraform.tfstate"
    dynamodb_table = "terraform-state"
    region         = "us-east-2"
    encrypt        = true
  }
}
