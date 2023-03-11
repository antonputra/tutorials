data "aws_iam_policy_document" "demo_arm64_csi" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.demo_arm64.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.demo_arm64.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "demo_arm64_eks_ebs_csi_driver" {
  assume_role_policy = data.aws_iam_policy_document.demo_arm64_csi.json
  name               = "eks-ebs-csi-driver"
}

resource "aws_iam_role_policy_attachment" "amazon_ebs_csi_driver" {
  role       = aws_iam_role.demo_arm64_eks_ebs_csi_driver.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

data "aws_iam_policy_document" "demo_amd64_csi" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.demo_amd64.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.demo_amd64.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "demo_amd64_eks_ebs_csi_driver" {
  assume_role_policy = data.aws_iam_policy_document.demo_amd64_csi.json
  name               = "amd-eks-ebs-csi-driver"
}

resource "aws_iam_role_policy_attachment" "demo_amd64_amazon_ebs_csi_driver" {
  role       = aws_iam_role.demo_amd64_eks_ebs_csi_driver.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}
