resource "google_project_service" "compute" {
  project = google_project.antonputra_host.project_id
  service = "compute.googleapis.com"
}

resource "google_project_service" "dns" {
  project = google_project.antonputra_host.project_id
  service = "dns.googleapis.com"
}

resource "google_compute_network" "main" {
  project                         = google_project.antonputra_host.project_id
  name                            = "main"
  routing_mode                    = "REGIONAL"
  auto_create_subnetworks         = false
  delete_default_routes_on_create = true

  depends_on = [google_project_service.compute]
}

resource "google_compute_shared_vpc_host_project" "host" {
  project = google_project.antonputra_host.project_id
}

resource "google_compute_shared_vpc_service_project" "service" {
  host_project    = google_project.antonputra_host.project_id
  service_project = google_project.antonputra_service.project_id

  depends_on = [google_compute_shared_vpc_host_project.host]
}
