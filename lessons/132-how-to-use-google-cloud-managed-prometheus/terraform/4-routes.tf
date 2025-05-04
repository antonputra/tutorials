resource "google_compute_route" "internet" {
  name             = "internet"
  dest_range       = "0.0.0.0/0"
  network          = google_compute_network.main.name
  next_hop_gateway = "default-internet-gateway"
}
