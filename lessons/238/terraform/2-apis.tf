# resource "google_project_service" "compute" {
#   service = "compute.googleapis.com"

#   disable_on_destroy = false
# }

# resource "google_project_service" "container" {
#   service = "container.googleapis.com"

#   disable_on_destroy = false
# }

# resource "google_project_service" "logging" {
#   service = "logging.googleapis.com"

#   disable_on_destroy = false
# }

# resource "google_project_service" "secretmanager" {
#   service = "secretmanager.googleapis.com"

#   disable_on_destroy = false
# }

resource "google_project_service" "api" {
  for_each = toset(local.apis)
  service  = each.key

  disable_on_destroy = false
}
