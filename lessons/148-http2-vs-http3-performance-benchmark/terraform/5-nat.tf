resource "google_compute_router" "router" {
  project = google_project.antonputra_host.project_id
  name    = "router"
  region  = google_compute_subnetwork.private.region
  network = google_compute_network.main.id
}

resource "google_compute_address" "nat" {
  project      = google_project.antonputra_host.project_id
  name         = "nat"
  address_type = "EXTERNAL"
  network_tier = "PREMIUM"
}

resource "google_compute_router_nat" "nat" {
  project                            = google_project.antonputra_host.project_id
  name                               = "nat"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "MANUAL_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  nat_ips                            = [google_compute_address.nat.self_link]

  subnetwork {
    name                    = google_compute_subnetwork.private.self_link
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}
