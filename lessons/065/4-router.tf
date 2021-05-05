# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router
resource "google_compute_router" "router" {
  name    = "router"
  region  = "us-west2"
  project = google_compute_shared_vpc_host_project.host.project
  network = google_compute_network.main.self_link
}
