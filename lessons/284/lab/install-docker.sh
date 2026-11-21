#!/bin/bash
# install-docker.sh: Docker Engine from Docker's own apt repository, as its install page says:
# https://docs.docker.com/engine/install/ubuntu/ (read 18 Nov 2026). Mission 9 of the lab.
set -e
sudo apt-get -o DPkg::Lock::Timeout=300 update -qq
sudo env DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=300 install -y -qq ca-certificates curl > /dev/null
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get -o DPkg::Lock::Timeout=300 update -qq
sudo env DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=300 install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin > /dev/null
dpkg-query -W docker-ce docker-ce-cli containerd.io docker-buildx-plugin
