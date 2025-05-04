resource "kubectl_manifest" "gateway_ns" {
  yaml_body = file("../k8s/gateway-ns.yaml")

  depends_on = [kubectl_manifest.mesh]
}
