# Install manually
# helm repo add argo https://argoproj.github.io/argo-helm
# helm repo update
# helm install argocd --namespace argocd --create-namespace --version 5.46.8 --values terraform/values/argocd.yaml argo/argo-cd
resource "helm_release" "argocd" {
  name = "argocd"

  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  create_namespace = true
  version          = "5.46.8"
  timeout          = 600

  values = [file("values/argocd.yaml")]
}
