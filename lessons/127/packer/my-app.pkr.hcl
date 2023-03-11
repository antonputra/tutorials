packer {
  required_plugins {
    amazon = {
      version = "~> v1.1.4"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

source "amazon-ebs" "my-app" {
  ami_name      = "my-app-{{ timestamp }}"
  instance_type = "t3.small"
  region        = "us-east-1"
  subnet_id     = "subnet-0849265f27f387c50"

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }

  ssh_username = "ubuntu"

  tags = {
    Name = "My App"
  }
}

build {
  sources = ["source.amazon-ebs.my-app"]

  provisioner "file" {
    destination = "/tmp"
    source      = "files"
  }

  provisioner "shell" {
    script = "scripts/bootstrap.sh"
  }

  provisioner "shell" {
    inline = [
      "sudo mv /tmp/files/my-app.service /etc/systemd/system/my-app.service",
      "sudo systemctl start my-app",
      "sudo systemctl enable my-app"
    ]
  }

  # Requires inspec to be installed on the host system: https://github.com/inspec/inspec
  # For mac, run "brew install chef/chef/inspec"
  provisioner "inspec" {
    inspec_env_vars = ["CHEF_LICENSE=accept"]
    profile         = "inspec"
    extra_arguments = ["--sudo", "--reporter", "html:/tmp/my-app-index.html"]
  }
}
