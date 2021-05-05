# Google Cloud Platform Provider
# https://registry.terraform.io/providers/hashicorp/google/latest/docs
provider "google" {
  region = "us-west2"
}

# https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/integer
resource "random_integer" "int" {
  min = 100
  max = 1000000
}
