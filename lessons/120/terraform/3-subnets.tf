# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_subnetwork
resource "google_compute_subnetwork" "private" {
  name                     = "private"
  region                   = local.region
  ip_cidr_range            = "10.0.0.0/18"
  stack_type               = "IPV4_ONLY"
  network                  = google_compute_network.main.id
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "public" {
  name          = "public"
  region        = local.region
  ip_cidr_range = "10.0.64.0/18"
  stack_type    = "IPV4_ONLY"
  network       = google_compute_network.main.id
}
