resource "aws_lambda_function" "go_gs" {
  function_name = "gs-resizer"

  memory_size = 1024
  timeout     = 60

  s3_bucket = aws_s3_bucket.functions.id
  s3_key    = aws_s3_object.lambda_go_gs.key

  environment {
    variables = {
      BUCKET_NAME = google_storage_bucket.images.id
    }
  }

  runtime = "go1.x"
  handler = "main"

  source_code_hash = data.archive_file.lambda_go_gs.output_base64sha256

  role = aws_iam_role.go_lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "go_gs" {
  name = "/aws/lambda/${aws_lambda_function.go_gs.function_name}"

  retention_in_days = 14
}

data "archive_file" "lambda_go_gs" {
  type = "zip"

  source_dir  = "../${path.module}/functions/aws-gs-resizer/target/"
  output_path = "../${path.module}/functions/aws-gs-resizer.zip"
}

resource "aws_s3_object" "lambda_go_gs" {
  bucket = aws_s3_bucket.functions.id

  key    = "aws-fs-resizer.zip"
  source = data.archive_file.lambda_go_gs.output_path

  source_hash = filemd5(data.archive_file.lambda_go_gs.output_path)
}

resource "aws_lambda_function_url" "lambda_go_gs" {
  function_name      = aws_lambda_function.go_gs.function_name
  authorization_type = "NONE"
}

output "aws_gs_resizer_url" {
  value = aws_lambda_function_url.lambda_go_gs.function_url
}
