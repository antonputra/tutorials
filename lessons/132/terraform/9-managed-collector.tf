resource "google_service_account" "collector" {
  account_id = "collector"
}

resource "google_service_account_iam_member" "collector" {
  service_account_id = google_service_account.collector.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${local.project_id}.svc.id.goog[gmp-system/collector]"
}

resource "google_project_iam_member" "collector" {
  project = local.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.collector.email}"

  depends_on = [
    google_service_account.collector
  ]
}
