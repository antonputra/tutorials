resource "aws_iam_instance_profile" "monitoring" {
  name = "monitoring"
  role = aws_iam_role.monitoring.name
}

resource "aws_iam_role" "monitoring" {
  name = "monitoring"

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

resource "aws_iam_role_policy_attachment" "monitoring" {
  role       = aws_iam_role.monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

resource "aws_instance" "monitoring" {
  ami                  = data.aws_ami.ubuntu_jammy.id
  key_name             = "devops"
  instance_type        = "t3a.small"
  subnet_id            = aws_subnet.public_us_east_1a.id
  iam_instance_profile = aws_iam_instance_profile.monitoring.name

  vpc_security_group_ids = [
    aws_security_group.ssh.id,
    aws_security_group.monitoring.id
  ]

  tags = {
    Name          = "monitoring.antonputra.com"
    service       = "monitoring"
    node-exporter = "true"
  }
}
