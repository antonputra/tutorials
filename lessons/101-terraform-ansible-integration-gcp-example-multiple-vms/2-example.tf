locals {
  project_id       = "devopsbyexample-325402"
  network          = "default"
  image            = "ubuntu-2004-focal-v20211212"
  ssh_user         = "ansible"
  private_key_path = "~/.ssh/ansbile_ed25519"

  web_servers = {
    nginx-000-staging = {
      machine_type = "e2-micro"
      zone         = "us-central1-a"
    }
    nginx-001-staging = {
      machine_type = "e2-micro"
      zone         = "us-central1-b"
    }
  }
}

provider "google" {
  project = local.project_id
  region  = "us-central1"
}

resource "google_service_account" "nginx" {
  account_id = "nginx-demo"
}

resource "google_compute_firewall" "web" {
  name    = "web-access"
  network = local.network

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges           = ["0.0.0.0/0"]
  target_service_accounts = [google_service_account.nginx.email]
}

resource "google_compute_instance" "nginx" {
  for_each = local.web_servers

  name         = each.key
  machine_type = each.value.machine_type
  zone         = each.value.zone

  boot_disk {
    initialize_params {
      image = local.image
    }
  }

  network_interface {
    network = local.network
    access_config {}
  }

  service_account {
    email  = google_service_account.nginx.email
    scopes = ["cloud-platform"]
  }

  provisioner "remote-exec" {
    inline = ["echo 'Wait until SSH is ready'"]

    connection {
      type        = "ssh"
      user        = local.ssh_user
      private_key = file(local.private_key_path)
      host        = self.network_interface.0.access_config.0.nat_ip
    }
  }

  provisioner "local-exec" {
    command = "ansible-playbook  -i ${self.network_interface.0.access_config.0.nat_ip}, --private-key ${local.private_key_path} nginx.yaml"
  }
}

output "nginx_ips" {
  value = {
    for k, v in google_compute_instance.nginx : k => "http://${v.network_interface.0.access_config.0.nat_ip}"
  }
}
