resource "aws_iam_role" "go_custom_lambda_exec" {
  name = "go-custom-lambda"

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

resource "aws_iam_policy" "go_custom_s3_bucket_access" {
  name = "goCustomS3BucketAccess"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::${aws_s3_bucket.images_bucket.id}/*"
      },
    ]
  })
}

resource "aws_iam_policy" "go_custom_dynamodb_access" {
  name = "goCustomDynamoDBAccess"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:DeleteItem",
          "dynamodb:PutItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:BatchGetItem",
          "dynamodb:DescribeTable",
          "dynamodb:ConditionCheckItem"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:dynamodb:*:*:table/images"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "go_custom_lambda_policy" {
  role       = aws_iam_role.go_custom_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "go_custom_s3_bucket_access" {
  role       = aws_iam_role.go_custom_lambda_exec.name
  policy_arn = aws_iam_policy.go_custom_s3_bucket_access.arn
}

resource "aws_iam_role_policy_attachment" "go_custom_dynamodb_access" {
  role       = aws_iam_role.go_custom_lambda_exec.name
  policy_arn = aws_iam_policy.go_custom_dynamodb_access.arn
}

resource "aws_lambda_function" "go_custom" {
  function_name = "go-custom"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_go_custom.key

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.images_bucket.id
    }
  }

  runtime = "provided.al2"
  handler = "bootstrap"

  source_code_hash = data.archive_file.lambda_go_custom.output_base64sha256

  role = aws_iam_role.go_custom_lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "go_custom" {
  name = "/aws/lambda/${aws_lambda_function.go_custom.function_name}"

  retention_in_days = 14
}

data "archive_file" "lambda_go_custom" {
  type = "zip"

  source_dir  = "../${path.module}/functions/go/target/custom"
  output_path = "../${path.module}/functions/go-custom.zip"
}

resource "aws_s3_object" "lambda_go_custom" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "go-custom.zip"
  source = data.archive_file.lambda_go_custom.output_path

  source_hash = filemd5(data.archive_file.lambda_go_custom.output_path)
}

resource "aws_lambda_function_url" "lambda_go_custom" {
  function_name      = aws_lambda_function.go_custom.function_name
  authorization_type = "NONE"
}

output "go_custom_lambda_url" {
  value = aws_lambda_function_url.lambda_go_custom.function_url
}
