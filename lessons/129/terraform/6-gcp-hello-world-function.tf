data "archive_file" "hello_world" {
  type = "zip"

  source_dir  = "../${path.module}/functions/gcp-hello-world/"
  output_path = "../${path.module}/functions/gcp-hello-world.zip"
}

resource "google_storage_bucket_object" "hello_world" {
  name   = "gcp-hello-world.zip"
  bucket = google_storage_bucket.functions.name
  source = data.archive_file.hello_world.output_path

  detect_md5hash = filemd5(data.archive_file.hello_world.output_path)
}

resource "google_cloudfunctions2_function" "hello_world" {
  name     = "hello-world"
  location = "us-east4"

  build_config {
    runtime     = "go119"
    entry_point = "HelloWorld"
    source {
      storage_source {
        bucket = google_storage_bucket.functions.name
        object = google_storage_bucket_object.hello_world.name
      }
    }
  }

  service_config {
    available_memory   = "1G"
    timeout_seconds    = 60
    max_instance_count = 100
  }

  depends_on = [
    google_project_service.cloudfunctions,
    google_project_service.run,
    google_project_service.artifactregistry,
    google_project_service.cloudbuild,
  ]
}

resource "google_cloud_run_service_iam_member" "hello_world_member" {
  project  = google_cloudfunctions2_function.hello_world.project
  location = google_cloudfunctions2_function.hello_world.location
  service  = google_cloudfunctions2_function.hello_world.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "gcp_hello_world_url" {
  value = google_cloudfunctions2_function.hello_world.service_config[0].uri
}
