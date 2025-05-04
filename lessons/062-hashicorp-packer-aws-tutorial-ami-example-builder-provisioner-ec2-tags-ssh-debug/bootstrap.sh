#!/bin/bash

set -e

sudo apt-get -y update
sudo apt-get -y install nginx
sudo mkdir -p /var/www/devopsbyexample.io/html
sudo chmod -R 755 /var/www/devopsbyexample.io
sudo mv /tmp/index.html /var/www/devopsbyexample.io/html/index.html
sudo mv /tmp/devopsbyexample.io /etc/nginx/sites-available/devopsbyexample.io
sudo ln -s /etc/nginx/sites-available/devopsbyexample.io /etc/nginx/sites-enabled/
