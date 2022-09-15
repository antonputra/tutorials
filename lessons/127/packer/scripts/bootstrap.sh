#!/bin/bash

set -e

sudo apt-get -y install golang-go
go install github.com/antonputra/tutorials/lessons/127/my-app@main
