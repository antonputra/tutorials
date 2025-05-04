data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_sns_topic" "alarms" {
  name = "alarms"

  policy = <<EOF
{
  "Version": "2008-10-17",
  "Id": "prometheus",
  "Statement": [
    {
      "Sid": "Allow_Publish_Alarms",
      "Effect": "Allow",
      "Principal": {
        "Service": "aps.amazonaws.com"
      },
      "Action": [
        "sns:Publish",
        "sns:GetTopicAttributes"
      ],
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "${aws_prometheus_workspace.demo.arn}"
        },
        "StringEquals": {
          "AWS:SourceAccount": "${data.aws_caller_identity.current.account_id}"
        }
      },
      "Resource": "arn:aws:sns:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:alarms"
    }
  ]
}
EOF
}
