resource "aws_iam_role" "go_lambda_exec" {
  name = "go-lambda"

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

resource "aws_iam_policy" "go_s3_bucket_access" {
  name = "goS3BucketAccess"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "s3:*"
        Effect   = "Allow"
        Resource = "arn:aws:s3:::${aws_s3_bucket.images.id}/*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "go_lambda_policy" {
  role       = aws_iam_role.go_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "go_s3_bucket_access" {
  role       = aws_iam_role.go_lambda_exec.name
  policy_arn = aws_iam_policy.go_s3_bucket_access.arn
}

resource "aws_lambda_function" "go" {
  function_name = "resizer"

  memory_size = 1024
  timeout     = 60

  s3_bucket = aws_s3_bucket.functions.id
  s3_key    = aws_s3_object.lambda_go.key

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.images.id
    }
  }

  runtime = "go1.x"
  handler = "main"

  source_code_hash = data.archive_file.lambda_go.output_base64sha256

  role = aws_iam_role.go_lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "go" {
  name = "/aws/lambda/${aws_lambda_function.go.function_name}"

  retention_in_days = 14
}

data "archive_file" "lambda_go" {
  type = "zip"

  source_dir  = "../${path.module}/functions/aws-resizer/target/"
  output_path = "../${path.module}/functions/aws-resizer.zip"
}

resource "aws_s3_object" "lambda_go" {
  bucket = aws_s3_bucket.functions.id

  key    = "aws-resizer.zip"
  source = data.archive_file.lambda_go.output_path

  source_hash = filemd5(data.archive_file.lambda_go.output_path)
}

resource "aws_lambda_function_url" "lambda_go" {
  function_name      = aws_lambda_function.go.function_name
  authorization_type = "NONE"
}

output "aws_resizer_url" {
  value = aws_lambda_function_url.lambda_go.function_url
}
