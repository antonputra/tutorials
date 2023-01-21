resource "google_compute_route" "internet" {
  project          = google_project.antonputra_host.project_id
  name             = "internet"
  dest_range       = "0.0.0.0/0"
  network          = google_compute_network.main.name
  next_hop_gateway = "default-internet-gateway"
}
