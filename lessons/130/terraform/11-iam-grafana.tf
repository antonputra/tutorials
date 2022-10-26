data "aws_iam_policy_document" "grafana_demo" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:monitoring:grafana"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "grafana_demo" {
  assume_role_policy = data.aws_iam_policy_document.grafana_demo.json
  name               = "grafana-demo"
}

resource "aws_iam_role_policy_attachment" "grafana_demo_query_access" {
  role       = aws_iam_role.grafana_demo.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonPrometheusQueryAccess"
}
