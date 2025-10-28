resource "aws_instance" "postgres" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  monitoring = false
  subnet_id  = module.vpc.private_subnets[0]

  vpc_security_group_ids = [aws_security_group.postgres.id]

  tags = {
    Name = "${local.env}-postgres"
  }
}
