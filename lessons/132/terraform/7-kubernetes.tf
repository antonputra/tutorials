resource "google_container_cluster" "main" {
  provider = google-beta
  name     = "main"
  location = "us-central1-a"

  remove_default_node_pool = true
  initial_node_count       = 1
  networking_mode          = "VPC_NATIVE"
  network                  = google_compute_network.main.self_link
  subnetwork               = google_compute_subnetwork.private.self_link

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods-ip-range"
    services_secondary_range_name = "services-ip-range"
  }

  workload_identity_config {
    workload_pool = "${local.project_id}.svc.id.goog"
  }

  private_cluster_config {
    master_ipv4_cidr_block  = "192.168.0.0/28"
    enable_private_nodes    = true
    enable_private_endpoint = false
  }

  monitoring_config {

    enable_components = ["SYSTEM_COMPONENTS"]

    managed_prometheus {
      enabled = true
    }
  }
}
