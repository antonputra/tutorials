variable "ami_name" {
  type = string
}
// AMI Builder (EBS backed)
// https://www.packer.io/docs/builders/amazon/ebs
source "amazon-ebs" "nginx" {
  ami_name      = var.ami_name
  source_ami    = "ami-042e8287309f5df03"
  instance_type = "t2.micro"
  subnet_id     = "subnet-0c3b9c3488903ebb9"
  ssh_username  = "ubuntu"
}

build {
  sources = ["source.amazon-ebs.nginx"]

  provisioner "file" {
    destination = "/tmp/"
    source      = "./index.html"
  }

  provisioner "file" {
    destination = "/tmp/"
    source      = "./devopsbyexample.io"
  }

  provisioner "shell" {
    script = "./bootstrap.sh"
  }
}
