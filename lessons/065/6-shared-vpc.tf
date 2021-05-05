# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_shared_vpc_host_project
resource "google_compute_shared_vpc_host_project" "host" {
  project = google_project.host-staging.number
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_shared_vpc_service_project
resource "google_compute_shared_vpc_service_project" "service" {
  host_project    = "${local.host_project}-${random_integer.int.result}"
  service_project = "${local.service_project}-${random_integer.int.result}"

  depends_on = [google_compute_shared_vpc_host_project.host]
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_service
resource "google_project_service" "host" {
  for_each = local.project_apis

  project = google_compute_shared_vpc_host_project.host.project
  service = each.value
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_service
resource "google_project_service" "service" {
  for_each = local.project_apis

  project = google_project.k8s-staging.number
  service = each.value
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_subnetwork_iam
resource "google_compute_subnetwork_iam_binding" "binding" {
  project    = google_compute_shared_vpc_host_project.host.project
  region     = google_compute_subnetwork.private.region
  subnetwork = google_compute_subnetwork.private.name

  role = "roles/compute.networkUser"
  members = [
    "user:me@antonputra.com",
    "serviceAccount:${google_service_account.k8s-staging.email}",
    "serviceAccount:${google_project.k8s-staging.number}@cloudservices.gserviceaccount.com",
    "serviceAccount:service-${google_project.k8s-staging.number}@container-engine-robot.iam.gserviceaccount.com"
  ]
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_iam
resource "google_project_iam_binding" "container-engine" {
  project = google_compute_shared_vpc_host_project.host.project
  role    = "roles/container.hostServiceAgentUser"

  members = [
    "serviceAccount:service-${google_project.k8s-staging.number}@container-engine-robot.iam.gserviceaccount.com",
  ]
  depends_on = [google_project_service.service]
}
