resource "google_compute_subnetwork" "public" {
  project                  = google_project.antonputra_host.project_id
  name                     = "public"
  ip_cidr_range            = "10.0.0.0/18"
  region                   = "us-central1"
  network                  = google_compute_network.main.id
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "private" {
  project                  = google_project.antonputra_host.project_id
  name                     = "private"
  ip_cidr_range            = "10.0.64.0/18"
  region                   = "us-central1"
  network                  = google_compute_network.main.id
  private_ip_google_access = true
}
