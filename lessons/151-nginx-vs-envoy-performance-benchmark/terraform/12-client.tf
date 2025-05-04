resource "aws_iam_instance_profile" "prometheus" {
  name = "prometheus"
  role = aws_iam_role.prometheus.name
}

resource "aws_iam_role" "prometheus" {
  name = "prometheus"

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

resource "aws_iam_role_policy_attachment" "prometheus" {
  role       = aws_iam_role.prometheus.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

resource "aws_instance" "client" {
  ami                  = data.aws_ami.ubuntu_jammy.id
  instance_type        = "m6a.large"
  subnet_id            = aws_subnet.public_us_east_1a.id
  iam_instance_profile = aws_iam_instance_profile.prometheus.name
  key_name             = "devops" # TODO: update to yours

  vpc_security_group_ids = [
    aws_security_group.client.id,
    aws_security_group.ssh.id
  ]

  tags = {
    Name          = "client"
    service       = "client"
    node-exporter = "true"
  }
}
