terraform {
  source = "../2-part"
}

locals {
  db_creds = yamldecode(sops_decrypt_file(("db-creds.yml")))
}

inputs = {
  username = local.db_creds.username
  password = local.db_creds.password
}
