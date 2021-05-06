# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router
resource "google_compute_router" "router" {
  name    = "router"
  region  = local.region
  project = local.host_project_id
  network = google_compute_network.main.self_link
}
