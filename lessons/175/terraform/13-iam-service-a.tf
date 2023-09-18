data "aws_iam_policy_document" "service_a" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:service-a:service-a"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "service_a" {
  assume_role_policy = data.aws_iam_policy_document.service_a.json
  name               = "${local.env}-${local.eks_name}-eks-service-a"
}

resource "aws_iam_policy" "service_a" {
  policy = file("./proxy-auth.json")
  name   = "AppMeshServiceAAccess"
}

resource "aws_iam_role_policy_attachment" "service_a" {
  role       = aws_iam_role.service_a.name
  policy_arn = aws_iam_policy.service_a.arn
}

output "iam_service_a_arn" {
  value = aws_iam_role.service_a.arn
}
