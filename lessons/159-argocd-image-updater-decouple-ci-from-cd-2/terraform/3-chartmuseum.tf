# helm repo add chartmuseum https://chartmuseum.github.io/charts
# helm install chartmuseum -n chartmuseum --create-namespace chartmuseum/chartmuseum --version 3.9.3 -f terraform/values/chartmuseum.yaml
resource "helm_release" "chartmuseum" {
  name = "chartmuseum"

  repository       = "https://chartmuseum.github.io/charts"
  chart            = "chartmuseum"
  namespace        = "chartmuseum"
  create_namespace = true
  version          = "3.9.3"

  values = [file("values/chartmuseum.yaml")]
}
