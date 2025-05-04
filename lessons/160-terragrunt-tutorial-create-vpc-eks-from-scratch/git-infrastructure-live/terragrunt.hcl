remote_state {
  backend = "s3"
  generate = {
    path      = "state.tf"
    if_exists = "overwrite_terragrunt"
  }

  config = {
    profile = "anton"
    role_arn = "arn:aws:iam::424432388155:role/terraform"
    bucket = "antonputra-terraform-state"

    key = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-table"
  }
}

generate "provider" {
  path = "provider.tf"
  if_exists = "overwrite_terragrunt"

  contents = <<EOF
provider "aws" {
  region  = "us-east-1"
  profile = "anton"
  
  assume_role {
    session_name = "leson-160"
    role_arn = "arn:aws:iam::424432388155:role/terraform"
  }
}
EOF
}
