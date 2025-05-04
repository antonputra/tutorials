resource "google_container_node_pool" "general" {
  name       = "general"
  location   = "us-central1-a"
  cluster    = google_container_cluster.main.name
  node_count = 2

  node_config {
    machine_type = "e2-standard-2"

    service_account = google_service_account.kubernetes_node.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
