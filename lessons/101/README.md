# Terraform Ansible Integration: GCP Example & Multiple VMs

[YouTube Tutorial](https://youtu.be/wVq5fwx1OQU)

## Prerequisites

- Ansible
- Terraform

## Generate SSH Key Pair

- Run the following command to generate elliptic curve ssh key pair

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ansbile_ed25519 -C ansible
```

- **Optionally**, you can generate RSA key pair

```bash
ssh-keygen -t rsa -f ~/.ssh/ansbile -C ansible -b 2048
```

## Add SSH Key to GCP Project

- Go to compute engine section
- Click Metadata
- Select `SSH KEYS` tab and click `ADD SSH KEY`
- Upload public `ansbile_ed25519.pub` key
  - `cat ~/.ssh/ansbile_ed25519.pub`

## Create Ansible Playbook for Nginx Installation

- Create `roles/nginx/tasks/main.yaml` task
- Create `nginx.yaml` playbook
- Create Ansible config `ansible.cfg` to skip host key verification

## Create Terraform Ansible Integration Example

- Create terraform file `1-example.tf`
- Open default firewall rules
- Verify that you have Terraform and Ansible installed

```bash
command -v terraform
command -v ansible-playbook
```

- Run `terraform init` to download provider and plugins
- Run `terraform apply` to create Nginx instance in GCP

## Provision Multiple VMs

- Destroy previous example `terraform destroy`
- Copy `1-example.tf` -> `2-example.tf`
- Rename `1-example.tf` -> `1-example.tf.bac`
- Add local variable
```
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
```

```
  for_each = local.web_servers

  name         = each.key
  machine_type = each.value.machine_type
  zone         = each.value.zone
```

```
host = self.network_interface.0.access_config.0.nat_ip
```
```
command = "ansible-playbook  -i ${self.network_interface.0.access_config.0.nat_ip}, --private-key ${local.private_key_path} nginx.yaml"
```

```
output "nginx_ips" {
  value = {
    for k, v in google_compute_instance.nginx : k => "http://${v.network_interface.0.access_config.0.nat_ip}"
  }
}
```

- Run `terraform apply`

## Clean Up

- `terraform destroy`
- rm ~/.ssh/ansbile*
- Delete SSH public key from GCP project
