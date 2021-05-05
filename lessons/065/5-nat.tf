resource "google_compute_router_nat" "mist_nat" {
  name                               = "nat"
  project                            = google_compute_shared_vpc_host_project.host.project
  router                             = google_compute_router.router.name
  region                             = "us-west2"
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  depends_on = [google_compute_subnetwork.private]
}
