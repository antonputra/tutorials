# Create an IAM role for the SNS with access to CloudWatch
resource "aws_iam_role" "sns_logs" {
  name = "sns-logs"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

# Allow SNS to write logs to CloudWatch
resource "aws_iam_role_policy_attachment" "sns_logs" {
  role       = aws_iam_role.sns_logs.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonSNSRole"
}

# Create an SNS topic to receive notifications from CloudWatch
resource "aws_sns_topic" "alarms" {
  name = "alarms"

  # Important! Only for testing, set to log every single message 
  # For production, set it to 0 or close
  lambda_success_feedback_sample_rate = 100

  lambda_failure_feedback_role_arn = aws_iam_role.sns_logs.arn
  lambda_success_feedback_role_arn = aws_iam_role.sns_logs.arn
}
