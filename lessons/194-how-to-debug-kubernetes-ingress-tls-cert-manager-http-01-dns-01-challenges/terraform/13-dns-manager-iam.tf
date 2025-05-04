# Optional: Used for the DNS-01 challenge.

data "aws_iam_policy_document" "dns_manager" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:cert-manager:cert-manager"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "dns_manager" {
  assume_role_policy = data.aws_iam_policy_document.dns_manager.json
  name               = "${local.env}-${local.eks_name}-dns-manager"
}

resource "aws_iam_policy" "dns_manager" {
  name = "dns_manager"
  path = "/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "route53:GetChange",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:route53:::change/*"
      },
      {
        Action = [
          "route53:ChangeResourceRecordSets",
          "route53:ListResourceRecordSets"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:route53:::hostedzone/*"
      },
      {
        Action = [
          "route53:ListHostedZonesByName"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dns_manager" {
  policy_arn = aws_iam_policy.dns_manager.arn
  role       = aws_iam_role.dns_manager.name
}
