data "aws_iam_policy_document" "service_b" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:service-b:service-b"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "service_b" {
  assume_role_policy = data.aws_iam_policy_document.service_b.json
  name               = "${local.env}-${local.eks_name}-eks-service-b"
}

resource "aws_iam_policy" "service_b" {
  policy = file("./proxy-auth.json")
  name   = "AppMeshServiceBAccess"
}

resource "aws_iam_role_policy_attachment" "service_b" {
  role       = aws_iam_role.service_b.name
  policy_arn = aws_iam_policy.service_b.arn
}

output "iam_service_b_arn" {
  value = aws_iam_role.service_b.arn
}
