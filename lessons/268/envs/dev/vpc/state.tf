terraform {
  backend "s3" {
    region       = ""
    bucket       = ""
    key          = "dev/vpc/terraform.tfstate"
    use_lockfile = true
    encrypt      = true
  }
}
