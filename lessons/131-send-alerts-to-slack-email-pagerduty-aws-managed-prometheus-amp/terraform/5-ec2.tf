resource "aws_iam_instance_profile" "prometheus_demo" {
  name = "prometheus-demo"
  role = aws_iam_role.prometheus_demo.name
}

resource "aws_iam_role" "prometheus_demo" {
  name = "prometheus-demo"
  path = "/"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow"
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "prometheus_demo_ingest_access" {
  role       = aws_iam_role.prometheus_demo.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonPrometheusRemoteWriteAccess"
}

resource "aws_iam_role_policy_attachment" "prometheus_ec2_access" {
  role       = aws_iam_role.prometheus_demo.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

resource "aws_security_group" "my_app" {
  name        = "my-app"
  description = "Allow My App Access"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Allow SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow Prometheus UI Access (only for demo)"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}

resource "aws_instance" "my_app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = "devops"
  subnet_id              = aws_subnet.public_us_east_1a.id
  vpc_security_group_ids = [aws_security_group.my_app.id]

  iam_instance_profile = aws_iam_instance_profile.prometheus_demo.name

  user_data = templatefile("bootstrap.sh.tpl",
    {
      prometheus_ver    = "2.39.1",
      node_exporter_ver = "1.4.0",
      remote_write_url  = aws_prometheus_workspace.demo.prometheus_endpoint
  })

  tags = {
    Name          = "my-app.example.pvt"
    node-exporter = "true"
  }
}

output "ec2_ip" {
  value = aws_instance.my_app.public_ip
}
