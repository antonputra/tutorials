resource "aws_lambda_function" "this" {
  function_name = "market-maker"
  role          = aws_iam_role.this.arn
  package_type  = "Image"
  image_uri     = "424432388155.dkr.ecr.ap-northeast-1.amazonaws.com/mexc/market-maker:${var.tag}"

  image_config {
    command = ["lambda_function.handler"]
  }

  memory_size = 128
  timeout     = 10

  architectures = ["arm64"]

  environment {
    variables = {
      MEXC_TOKEN = ""
    }
  }
}
