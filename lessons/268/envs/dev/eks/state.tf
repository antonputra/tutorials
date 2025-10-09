terraform {
  backend "s3" {
    region       = ""
    bucket       = ""
    key          = "dev/eks/terraform.tfstate"
    use_lockfile = true
    encrypt      = true
  }
}
