# Install Prometheus Adapter Manually
# kubectl apply -f monitoring/prometheus-adapter
data "kubectl_path_documents" "prometheus_adapter" {
  pattern = "../monitoring/prometheus-adapter/*.yaml"
}

resource "kubectl_manifest" "prometheus_adapter" {
  for_each  = toset(data.kubectl_path_documents.prometheus_adapter.documents)
  yaml_body = each.value

  depends_on = [helm_release.prometheus_operator_crds]
}
