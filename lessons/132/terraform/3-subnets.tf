resource "google_compute_subnetwork" "private" {
  name                     = "private"
  ip_cidr_range            = "10.0.0.0/19"
  region                   = "us-central1"
  network                  = google_compute_network.main.id
  private_ip_google_access = true
  stack_type               = "IPV4_ONLY"

  secondary_ip_range {
    range_name    = "pods-ip-range"
    ip_cidr_range = "172.16.0.0/14"
  }

  secondary_ip_range {
    range_name    = "services-ip-range"
    ip_cidr_range = "172.20.0.0/18"
  }
}
