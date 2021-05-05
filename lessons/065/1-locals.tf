# https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/integer
resource "random_integer" "int" {
  min = 1
  max = 1000000
}

locals {
  org_id               = "206720471760"
  billing_account      = "01FDA3-9697F3-6F05B8"
  host_project_name    = "host-staging"
  service_project_name = "k8s-staging"
  host_project_id      = "${local.host_project_name}-${random_integer.int.result}"
  service_project_id   = "${local.service_project_name}-${random_integer.int.result}"
  project_apis = {
    1 = "container.googleapis.com"
  }
  k8s_subnet_secondary_ip_ranges = {
    "pod-ip-range"      = "10.0.0.0/14",
    "services-ip-range" = "10.4.0.0/19"
  }
}
