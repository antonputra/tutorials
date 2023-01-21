resource "google_service_account" "nginx" {
  project    = google_project.antonputra_service.project_id
  account_id = "nginx-proxy"
}

resource "google_compute_firewall" "web" {
  name    = "web"
  project = google_project.antonputra_host.project_id
  network = google_compute_network.main.self_link

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "22"]
  }

  allow {
    protocol = "udp"
    ports    = ["443"]
  }

  source_ranges           = ["0.0.0.0/0"]
  target_service_accounts = [google_service_account.nginx.email]
}

resource "google_compute_instance" "nginx_http2" {
  project      = google_project.antonputra_service.project_id
  name         = "nginx-http2"
  machine_type = "n2-standard-2"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.public.self_link

    access_config {}
  }

  labels = {
    service = "nginx"
    service = "nginx_http2"
  }

  service_account {
    email  = google_service_account.nginx.email
    scopes = ["cloud-platform"]
  }
}

resource "google_compute_instance" "nginx_http3" {
  project      = google_project.antonputra_service.project_id
  name         = "nginx-http3"
  machine_type = "n2-standard-2"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.public.self_link

    access_config {}
  }

  labels = {
    service = "nginx_http3"
  }

  service_account {
    email  = google_service_account.nginx.email
    scopes = ["cloud-platform"]
  }
}
