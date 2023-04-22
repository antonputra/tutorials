#!/bin/bash

set -e

# Create user for Node Exporter
useradd --system --no-create-home --shell /bin/false node_exporter

# Download Node Exporter archive
wget https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz

# Extracts Node Exporter files
tar -xvf node_exporter-1.3.1.linux-amd64.tar.gz

# Move Node Exporter binary to the bin
mv node_exporter-1.3.1.linux-amd64/node_exporter /usr/local/bin/

# Configure Node Exporter to start automatically upon system boot
systemctl enable node_exporter

# Start Node Exporter
systemctl start node_exporter
