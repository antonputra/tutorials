resource "helm_release" "appmesh_gateway" {
  name = "appmesh-gateway"

  repository       = "https://aws.github.io/eks-charts"
  chart            = "appmesh-gateway"
  namespace        = "gateway"
  create_namespace = false
  version          = "0.1.5"

  set {
    name  = "serviceAccount.name"
    value = "appmesh-gateway"
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.appmesh_gateway.arn
  }

  set {
    name  = "service.port"
    value = 80
  }

  depends_on = [
    kubectl_manifest.mesh,
    kubectl_manifest.gateway_ns,
    helm_release.appmesh_controller,
    aws_iam_role_policy_attachment.aws_cloud_map_full_access_gateway,
    aws_iam_role_policy_attachment.aws_appmesh_full_access_gateway
  ]
}
