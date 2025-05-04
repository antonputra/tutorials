module "prometheus" {
  source = "git@github.com:antonputra/terraform-aws-prometheus.git//?ref=v0.0.1"

  vpc_id             = aws_vpc.main.id
  subnet_id          = aws_subnet.private_us_east_1a.id
  prometheus_version = "2.41.0"
  instance_type      = "t3a.small"
  disk_size          = 50
  prometheus_config  = <<EOT
---
global:
  scrape_interval: 5s
  evaluation_interval: 5s
scrape_configs:

- job_name: ec2-traefik-exporter
  ec2_sd_configs:
  - region: us-east-1
    port: 8082
    filters:
    - name: tag:traefik-exporter
      values:
      - true
  relabel_configs:
  - source_labels: [__meta_ec2_tag_Name]
    target_label: instance
  - regex: "__meta_ec2_tag_(.+)"
    action: labelmap

- job_name: ec2-nginx-exporter
  ec2_sd_configs:
  - region: us-east-1
    port: 9150
    filters:
    - name: tag:nginx-exporter
      values:
      - true
  relabel_configs:
  - source_labels: [__meta_ec2_tag_Name]
    target_label: instance
  - regex: "__meta_ec2_tag_(.+)"
    action: labelmap

- job_name: ec2-node-exporter
  ec2_sd_configs:
  - region: us-east-1
    port: 9100
    filters:
    - name: tag:node-exporter
      values:
      - true
  relabel_configs:
  - source_labels: [__meta_ec2_tag_Name]
    target_label: instance
  - regex: "__meta_ec2_tag_(.+)"
    action: labelmap
EOT
}

output "prometheus" {
  value = module.prometheus
}
