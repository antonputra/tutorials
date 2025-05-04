data "aws_iam_policy_document" "demo_arm64_prometheus" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.demo_arm64.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:monitoring:prometheus"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.demo_arm64.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "demo_arm64_prometheus" {
  assume_role_policy = data.aws_iam_policy_document.demo_arm64_prometheus.json
  name               = "arm64-prometheus-demo"
}

# OPTIONAL: only if you have standalone EC2 instances to scare
resource "aws_iam_role_policy_attachment" "demo_arm64_prometheus_ec2_access" {
  role       = aws_iam_role.demo_arm64_prometheus.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

data "aws_iam_policy_document" "demo_amd64_prometheus" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.demo_amd64.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:monitoring:prometheus"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.demo_amd64.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "demo_amd64_prometheus" {
  assume_role_policy = data.aws_iam_policy_document.demo_amd64_prometheus.json
  name               = "amd64-prometheus-demo"
}

# OPTIONAL: only if you have standalone EC2 instances to scare
resource "aws_iam_role_policy_attachment" "demo_amd64_prometheus_ec2_access" {
  role       = aws_iam_role.demo_amd64_prometheus.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}
