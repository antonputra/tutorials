resource "google_compute_firewall" "lb" {
  name        = "k8s-fw-abdca8a7bd83f4a84a8fb7a869242967"
  network     = google_compute_network.main.name
  project     = local.host_project_id
  description = "{\"kubernetes.io/service-name\":\"default/nginx\", \"kubernetes.io/service-ip\":\"35.235.121.183\"}"

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["gke-gke-08c5d5fb-node"]
}

resource "google_compute_firewall" "health" {
  name        = "k8s-9cf34e5201ee63aa-node-http-hc"
  network     = google_compute_network.main.name
  project     = local.host_project_id
  description = "{\"kubernetes.io/cluster-id\":\"9cf34e5201ee63aa\"}"

  allow {
    protocol = "tcp"
    ports    = ["10256"]
  }

  source_ranges = ["130.211.0.0/22", "209.85.152.0/22", "209.85.204.0/22", "35.191.0.0/16"]
  target_tags   = ["gke-gke-08c5d5fb-node"]
}
