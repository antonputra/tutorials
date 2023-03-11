data "aws_caller_identity" "current" {}

resource "aws_iam_policy" "allow_assume_developer_role" {
  name = "AllowAssumeDeveloperRole"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "${aws_iam_role.developer.arn}"
    }
  ]
}
POLICY
}

resource "aws_iam_role" "developer" {
  name = "developer"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Principal": {
            "AWS": "${data.aws_caller_identity.current.account_id}"
        },
        "Condition": {}
    }
  ]
}
POLICY
}

resource "aws_iam_policy" "eks_console_access" {
  name = "EKSConsoleAccess"

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "iam:PassedToService": "eks.amazonaws.com"
                }
            }
        }
    ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "developer_eks_console_access" {
  role       = aws_iam_role.developer.name
  policy_arn = aws_iam_policy.eks_console_access.arn
}

resource "kubectl_manifest" "cluster_role_reader" {
  yaml_body = <<-YAML
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: reader
rules:
- apiGroups: ["*"]
  resources: ["deployments", "configmaps", "pods", "secrets", "services"]
  verbs: ["get", "list", "watch"]
YAML

  depends_on = [aws_iam_role_policy_attachment.developer_eks_console_access]
}

resource "kubectl_manifest" "cluster_role_binding_reader" {
  yaml_body = <<-YAML
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: reader
subjects:
- kind: Group
  name: reader
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: reader
  apiGroup: rbac.authorization.k8s.io
YAML

  depends_on = [aws_iam_role_policy_attachment.developer_eks_console_access]
}
