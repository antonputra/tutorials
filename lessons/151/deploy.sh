#!/bin/bash

set -ex

cd terraform
terraform init
terraform apply --auto-approve

# Build app binaries
cd ../go-app
GOOS=linux GOARCH=amd64 go build -o target/rest-server cmd/rest-server/main.go
GOOS=linux GOARCH=amd64 go build -o target/grpc-server cmd/grpc-server/main.go

# Generate certificates
cd ../demo-certs
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=demo api-envoy-antonputra-pvt-csr.json | cfssljson -bare api-envoy-antonputra-pvt
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=demo api-nginx-antonputra-pvt-csr.json | cfssljson -bare api-nginx-antonputra-pvt

cd ../ansible
ansible-playbook -i aws_ec2.yaml --private-key ~/.ssh/devops.pem infra.yaml
