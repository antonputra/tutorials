resource "google_service_account" "k8s-staging" {
  project    = service_project_id
  account_id = "k8s-staging"

  depends_on = [google_project.k8s-staging]
}

# resource "google_container_cluster" "gke" {
#   name     = "gke"
#   location = "us-west2"
#   project = "${local.service_project}-${random_integer.int.result}"

#   networking_mode = "VPC_NATIVE"
#   network = google_compute_network.main.self_link

#   subnetwork                  = google_compute_subnetwork.private.self_link

#   remove_default_node_pool = true
#   initial_node_count       = 1

#   # master_authorized_networks_config {
#   #   cidr_blocks {
#   #     cidr_block   = "172.16.0.0/28"
#   #   }
#   # }

#   ip_allocation_policy {
#     cluster_secondary_range_name = "pod-ip-range"
#     services_secondary_range_name = "services-ip-range"
#   }

#   network_policy {
#     provider = "PROVIDER_UNSPECIFIED"
#     enabled  = false
#   }

#    private_cluster_config {
#     enable_private_endpoint = false
#     enable_private_nodes    = true
#     master_ipv4_cidr_block  = "172.16.0.0/28"
#   }
# }

# resource "google_container_node_pool" "general" {
#   name       = "general"
#   location   = "us-west2"
#   cluster    = google_container_cluster.gke.name
#   project = "${local.service_project}-${random_integer.int.result}"
#   node_count = 1

#    management {
#     auto_repair  = true
#     auto_upgrade = true
#   }

#   node_config {
#     machine_type = "e2-medium"

#     service_account = google_service_account.k8s-staging.email
#     oauth_scopes    = [
#       "https://www.googleapis.com/auth/cloud-platform"
#     ]
#   }
# }
