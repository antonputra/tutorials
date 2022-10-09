# Enable cloudfunctions GCP API.
resource "google_project_service" "cloudfunctions" {
  project = "devops-364717"
  service = "cloudfunctions.googleapis.com"
}

# Enable run GCP API.
resource "google_project_service" "run" {
  project = "devops-364717"
  service = "run.googleapis.com"
}

# Enable artifactregistry GCP API.
resource "google_project_service" "artifactregistry" {
  project = "devops-364717"
  service = "artifactregistry.googleapis.com"
}

# Enable cloudbuild GCP API.
resource "google_project_service" "cloudbuild" {
  project = "devops-364717"
  service = "cloudbuild.googleapis.com"
}
