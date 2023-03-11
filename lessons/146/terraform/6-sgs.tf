locals {
  my_public_ip = "67.182.47.121/32"
}

resource "aws_security_group" "ssh" {
  name   = "ssh"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "Allow SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.my_public_ip]
  }
}

resource "aws_security_group" "proxy" {
  name   = "proxy"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "Allow Web traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow Secure web traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description     = "Allow Node Exporter Access"
    from_port       = 9100
    to_port         = 9100
    protocol        = "tcp"
    security_groups = [aws_security_group.monitoring.id]
  }

  egress {
    description = "Allow ALL outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "myapp" {
  name   = "myapp"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "Allow Web traffic and metrics"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    security_groups = [
      aws_security_group.proxy.id,
      aws_security_group.monitoring.id
    ]
  }

  ingress {
    description     = "Allow Node Exporter Access"
    from_port       = 9100
    to_port         = 9100
    protocol        = "tcp"
    security_groups = [aws_security_group.monitoring.id]
  }

  egress {
    description = "Allow ALL outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "monitoring" {
  name   = "monitoring"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "Allow Prometheus Access"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = [local.my_public_ip]
  }

  ingress {
    description = "Allow Grafana Access"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = [local.my_public_ip]
  }

  egress {
    description = "Allow ALL outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "client" {
  name   = "client"
  vpc_id = aws_vpc.main.id

  ingress {
    description     = "Allow Node Exporter Access"
    from_port       = 9100
    to_port         = 9100
    protocol        = "tcp"
    security_groups = [aws_security_group.monitoring.id]
  }

  egress {
    description = "Allow ALL outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
