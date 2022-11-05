resource "google_project_service" "api" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com"
  ])

  service            = each.key
  disable_on_destroy = false
}
