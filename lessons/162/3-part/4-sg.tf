# Security group to allow inbound access to RDS PostgreSQL
resource "aws_security_group" "rds_security_group" {
  name        = "rds-postgresql-sg"
  description = "Allow inbound PostgreSQL access from a specific IP"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allows access from all IP addresses
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}