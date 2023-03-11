data "aws_iam_policy_document" "csi" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "eks_ebs_csi_driver" {
  assume_role_policy = data.aws_iam_policy_document.csi.json
  name               = "eks-ebs-csi-driver"
}

resource "aws_iam_role_policy_attachment" "amazon_ebs_csi_driver" {
  role       = aws_iam_role.eks_ebs_csi_driver.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

# Optional: only if you use your own KMS key to encrypt EBS volumes
# TODO: replace arn:aws:kms:us-east-1:424432388155:key/7a8ea545-e379-4ac5-8903-3f5ae22ea847 with your KMS key id arn!
# resource "aws_iam_policy" "eks_ebs_csi_driver_kms" {
#   name = "KMS_Key_For_Encryption_On_EBS"

#   policy = <<POLICY
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Effect": "Allow",
#       "Action": [
#         "kms:CreateGrant",
#         "kms:ListGrants",
#         "kms:RevokeGrant"
#       ],
#       "Resource": ["arn:aws:kms:us-east-1:424432388155:key/7a8ea545-e379-4ac5-8903-3f5ae22ea847"],
#       "Condition": {
#         "Bool": {
#           "kms:GrantIsForAWSResource": "true"
#         }
#       }
#     },
#     {
#       "Effect": "Allow",
#       "Action": [
#         "kms:Encrypt",
#         "kms:Decrypt",
#         "kms:ReEncrypt*",
#         "kms:GenerateDataKey*",
#         "kms:DescribeKey"
#       ],
#       "Resource": ["arn:aws:kms:us-east-1:424432388155:key/7a8ea545-e379-4ac5-8903-3f5ae22ea847"]
#     }
#   ]
# }
# POLICY
# }

# resource "aws_iam_role_policy_attachment" "amazon_ebs_csi_driver_kms" {
#   role       = aws_iam_role.eks_ebs_csi_driver.name
#   policy_arn = aws_iam_policy.eks_ebs_csi_driver_kms.arn
# }
