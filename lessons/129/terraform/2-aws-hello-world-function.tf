resource "aws_iam_role" "go_hello_lambda_exec" {
  name = "go-hello-lambda"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "go_hello_lambda_policy" {
  role       = aws_iam_role.go_hello_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "go_hello" {
  function_name = "hello-world"

  memory_size = 1024
  timeout     = 60

  s3_bucket = aws_s3_bucket.functions.id
  s3_key    = aws_s3_object.lambda_go_hello.key

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.images.id
    }
  }

  runtime = "go1.x"
  handler = "main"

  source_code_hash = data.archive_file.lambda_go_hello.output_base64sha256

  role = aws_iam_role.go_hello_lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "go_hello" {
  name = "/aws/lambda/${aws_lambda_function.go_hello.function_name}"

  retention_in_days = 14
}

data "archive_file" "lambda_go_hello" {
  type = "zip"

  source_dir  = "../${path.module}/functions/aws-hello-world/target/"
  output_path = "../${path.module}/functions/aws-hello-world.zip"
}

resource "aws_s3_object" "lambda_go_hello" {
  bucket = aws_s3_bucket.functions.id

  key    = "aws-hello-world.zip"
  source = data.archive_file.lambda_go_hello.output_path

  source_hash = filemd5(data.archive_file.lambda_go_hello.output_path)
}

resource "aws_lambda_function_url" "lambda_go_hello" {
  function_name      = aws_lambda_function.go_hello.function_name
  authorization_type = "NONE"
}

output "aws_hello_world_url" {
  value = aws_lambda_function_url.lambda_go_hello.function_url
}
