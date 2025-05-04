provider "aws" {
  region = "us-east-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0a695f0d95cefc163"
  instance_type = "t3.micro"
}

resource "aws_db_instance" "mydb" {
  db_name           = "mydb"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t4g.micro"
  allocated_storage = 10

  publicly_accessible = true
  skip_final_snapshot = true

  username = "root"
  password = "devops123"
}
