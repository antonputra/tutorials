resource "null_resource" "certs" {
  provisioner "local-exec" {
    command = "../vpa/gencerts.sh"
  }
}

# Install VPA Manually
# kubectl apply -f vpa
data "kubectl_path_documents" "vpa" {
  pattern = "../vpa/*.yaml"
}

resource "kubectl_manifest" "vpa" {
  for_each  = toset(data.kubectl_path_documents.vpa.documents)
  yaml_body = each.value

  depends_on = [null_resource.certs]
}
