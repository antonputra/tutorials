provider "aws" {
  region = "us-east-2"
}

terraform {
  backend "s3" {
    key = "staging/services/web/terraform.tfstate"
  }
}

resource "aws_security_group" "instance" {
  name = "web"

  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "example" {
  ami           = "ami-0a695f0d95cefc163"
  instance_type = "t3.micro"

  vpc_security_group_ids = [aws_security_group.instance.id]

  user_data = templatefile("user-data.sh", {
    server_port      = var.server_port
    postgres_address = data.terraform_remote_state.postgres.outputs.address
    postgres_port    = data.terraform_remote_state.postgres.outputs.port
  })

  user_data_replace_on_change = true
}

data "terraform_remote_state" "postgres" {
  backend = "s3"

  config = {
    bucket = "antonputra-terraform-state"
    key    = "staging/data-stores/postgres/terraform.tfstate"
    region = "us-east-2"
  }
}
