#!/bin/bash

sudo -s

# Install Prometheus
useradd --system --no-create-home --shell /bin/false prometheus
wget https://github.com/prometheus/prometheus/releases/download/v${prometheus_ver}/prometheus-${prometheus_ver}.linux-amd64.tar.gz
tar -xvf prometheus-${prometheus_ver}.linux-amd64.tar.gz
mkdir -p /data /etc/prometheus
mv prometheus-${prometheus_ver}.linux-amd64/prometheus prometheus-${prometheus_ver}.linux-amd64/promtool /usr/local/bin/

cat <<EOT > /etc/prometheus/prometheus.yml
---
global:
  scrape_interval: 15s
  evaluation_interval: 15s
remote_write:
- url: ${remote_write_url}api/v1/remote_write
  sigv4:
    region: us-east-1
  queue_config:
    max_samples_per_send: 1000
    max_shards: 200
    capacity: 2500
scrape_configs:
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

chown -R prometheus:prometheus /etc/prometheus/ /data/

cat <<EOT > /etc/systemd/system/prometheus-agent.service
[Unit]
Description=Prometheus Agent
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=0
StartLimitBurst=5

[Service]
User=prometheus
Group=prometheus
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --enable-feature=agent \
  --storage.agent.path=/data \
  --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
EOT

systemctl enable prometheus-agent
systemctl start prometheus-agent

# Install Node Exporter
useradd --system --no-create-home --shell /bin/false node_exporter
wget https://github.com/prometheus/node_exporter/releases/download/v${node_exporter_ver}/node_exporter-${node_exporter_ver}.linux-amd64.tar.gz
tar -xvf node_exporter-${node_exporter_ver}.linux-amd64.tar.gz
mv node_exporter-${node_exporter_ver}.linux-amd64/node_exporter /usr/local/bin/

cat <<EOT > /etc/systemd/system/node-exporter.service
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
User=node_exporter
Group=node_exporter
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOT

systemctl enable node-exporter
systemctl start node-exporter

# Install stress tool
apt-get update
apt install -y stress