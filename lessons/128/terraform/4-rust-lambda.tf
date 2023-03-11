resource "aws_iam_role" "rust_lambda_exec" {
  name = "rust-lambda"

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

resource "aws_iam_policy" "rust_s3_bucket_access" {
  name = "rustS3BucketAccess"

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

resource "aws_iam_policy" "rust_dynamodb_access" {
  name = "rustDynamoDBAccess"

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

resource "aws_iam_role_policy_attachment" "rust_lambda_policy" {
  role       = aws_iam_role.rust_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "rust_s3_bucket_access" {
  role       = aws_iam_role.rust_lambda_exec.name
  policy_arn = aws_iam_policy.rust_s3_bucket_access.arn
}

resource "aws_iam_role_policy_attachment" "rust_dynamodb_access" {
  role       = aws_iam_role.rust_lambda_exec.name
  policy_arn = aws_iam_policy.rust_dynamodb_access.arn
}

resource "aws_lambda_function" "rust" {
  function_name = "rust"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_rust.key

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.images_bucket.id
    }
  }

  runtime = "provided.al2"
  handler = "bootstrap"

  source_code_hash = data.archive_file.lambda_rust.output_base64sha256

  role = aws_iam_role.rust_lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "rust" {
  name = "/aws/lambda/${aws_lambda_function.rust.function_name}"

  retention_in_days = 14
}

data "archive_file" "lambda_rust" {
  type = "zip"

  source_dir  = "../${path.module}/functions/rust/target/lambda/rust"
  output_path = "../${path.module}/functions/rust.zip"
}

resource "aws_s3_object" "lambda_rust" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "rust.zip"
  source = data.archive_file.lambda_rust.output_path

  source_hash = filemd5(data.archive_file.lambda_rust.output_path)
}

resource "aws_lambda_function_url" "lambda_rust" {
  function_name      = aws_lambda_function.rust.function_name
  authorization_type = "NONE"
}

output "rust_lambda_url" {
  value = aws_lambda_function_url.lambda_rust.function_url
}
