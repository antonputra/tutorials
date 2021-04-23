#!/bin/bash

set -e

sudo -s
apt-get update
apt-get install -y nginx
systemctl enable nginx

echo "${file_content}!" > /var/www/html/index.nginx-debian.html

systemctl restart nginx