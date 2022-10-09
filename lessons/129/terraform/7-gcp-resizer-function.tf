data "archive_file" "go" {
  type = "zip"

  source_dir  = "../${path.module}/functions/gcp-resizer/"
  output_path = "../${path.module}/functions/gcp-resizer.zip"
}

resource "google_storage_bucket_object" "go" {
  name           = "gcp-resizer.zip"
  bucket         = google_storage_bucket.functions.name
  source         = data.archive_file.go.output_path
  detect_md5hash = filemd5(data.archive_file.go.output_path)
}

resource "google_service_account" "go" {
  account_id = "resizer"
}

resource "google_cloudfunctions2_function" "go" {
  name     = "resizer"
  location = "us-east4"

  build_config {
    runtime     = "go119"
    entry_point = "Resizer"
    source {
      storage_source {
        bucket = google_storage_bucket.functions.name
        object = google_storage_bucket_object.go.name
      }
    }
  }

  service_config {
    available_memory      = "1G"
    timeout_seconds       = 60
    max_instance_count    = 100
    service_account_email = google_service_account.go.email
    environment_variables = {
      BUCKET_NAME = google_storage_bucket.images.id
    }
  }

  depends_on = [
    google_project_service.cloudfunctions,
    google_project_service.run,
    google_project_service.artifactregistry,
    google_project_service.cloudbuild,
  ]
}

resource "google_cloud_run_service_iam_member" "go_member" {
  project  = google_cloudfunctions2_function.go.project
  location = google_cloudfunctions2_function.go.location
  service  = google_cloudfunctions2_function.go.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# resource "google_project_iam_member" "storage" {
#   project = google_cloudfunctions2_function.go.project
#   role    = "roles/storage.admin"
#   member  = "serviceAccount:${google_service_account.go.email}"
# }

resource "google_storage_bucket_iam_member" "storage" {
  bucket = google_storage_bucket.images.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.go.email}"
}

output "gcp_resizer_url" {
  value = google_cloudfunctions2_function.go.service_config[0].uri
}
