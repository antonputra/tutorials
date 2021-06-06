# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project
resource "google_project" "host-staging" {
  name                = local.host_project_name
  project_id          = local.host_project_id
  billing_account     = local.billing_account
  org_id              = local.org_id
  auto_create_network = false
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project
resource "google_project" "k8s-staging" {
  name                = local.service_project_name
  project_id          = local.service_project_id
  billing_account     = local.billing_account
  org_id              = local.org_id
  auto_create_network = false
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_service
resource "google_project_service" "host" {
  project = google_project.host-staging.number
  service = local.projects_api
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_service
resource "google_project_service" "service" {
  project = google_project.k8s-staging.number
  service = local.projects_api
}