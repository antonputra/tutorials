resource "aws_iam_role" "s3_lambda_exec" {
  name = "s3-lambda"

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

resource "aws_iam_role_policy_attachment" "s3_lambda_policy" {
  role       = aws_iam_role.s3_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "test_s3_bucket_access" {
  name        = "TestS3BucketAccess"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::${aws_s3_bucket.test.id}/*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_lambda_test_s3_bucket_access" {
  role       = aws_iam_role.s3_lambda_exec.name
  policy_arn = aws_iam_policy.test_s3_bucket_access.arn
}

resource "aws_lambda_function" "s3" {
  function_name = "s3"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_s3.key

  runtime = "nodejs16.x"
  handler = "function.handler"

  source_code_hash = data.archive_file.lambda_s3.output_base64sha256

  role = aws_iam_role.s3_lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "s3" {
  name = "/aws/lambda/${aws_lambda_function.s3.function_name}"

  retention_in_days = 14
}

data "archive_file" "lambda_s3" {
  type = "zip"

  source_dir  = "../${path.module}/s3"
  output_path = "../${path.module}/s3.zip"
}

resource "aws_s3_object" "lambda_s3" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "s3.zip"
  source = data.archive_file.lambda_s3.output_path
  
  source_hash = filemd5(data.archive_file.lambda_s3.output_path)
}
