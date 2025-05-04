resource "random_id" "lesson_id" {
  byte_length = 2
}

resource "google_project" "antonputra_host" {
  name                = "antonputra-host"
  project_id          = "antonputra-host-${random_id.lesson_id.dec}"
  billing_account     = "01FDA3-9697F3-6F05B8"
  org_id              = "206720471760"
  auto_create_network = false
}

resource "google_project" "antonputra_service" {
  name                = "antonputra-service"
  project_id          = "antonputra-service-${random_id.lesson_id.dec}"
  billing_account     = "01FDA3-9697F3-6F05B8"
  org_id              = "206720471760"
  auto_create_network = false
}
