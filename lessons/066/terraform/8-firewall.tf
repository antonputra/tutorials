# resource "google_compute_firewall" "lb" {
#   name        = "k8s-fw-a03235a41ae06427795708a009caf1bd"
#   network     = google_compute_network.main.name
#   project     = local.host_project_id
#   description = "{\"kubernetes.io/service-name\":\"default/nginx\", \"kubernetes.io/service-ip\":\"34.94.59.100\"}"

#   allow {
#     protocol = "tcp"
#     ports    = ["80"]
#   }

#   source_ranges = ["0.0.0.0/0"]
#   target_tags   = ["gke-gke-4a41046b-node"]
# }

# resource "google_compute_firewall" "health" {
#   name        = "k8s-fw-a03235a41ae06427795708a009caf1bd"
#   network     = google_compute_network.main.name
#   project     = local.host_project_id
#   description = "{\"kubernetes.io/cluster-id\":\"a8b97d61c4cfa047\"}"

#   allow {
#     protocol = "tcp"
#     ports    = ["10256"]
#   }

#   source_ranges = ["130.211.0.0/22", "209.85.152.0/22", "209.85.204.0/22", "35.191.0.0/16"]
#   target_tags   = ["gke-gke-4a41046b-node"]
# }
