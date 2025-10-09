terraform {
  backend "s3" {
    region       = ""
    bucket       = ""
    key          = "global/iam/terraform.tfstate"
    use_lockfile = true
    encrypt      = true
  }
}
