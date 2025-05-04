provider "aws" {
  region = "us-east-2"
}

terraform {
  backend "s3" {
    key = "staging/data-stores/postgres/terraform.tfstate"
  }
}

resource "aws_db_instance" "mydb" {
  db_name           = "mydb"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t4g.micro"
  allocated_storage = 10

  skip_final_snapshot = true
  publicly_accessible = true

  username = var.username
  password = var.password
}
