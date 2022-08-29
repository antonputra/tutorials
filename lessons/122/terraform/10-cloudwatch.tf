# Create a CloudWatch alarm to trigger an alert when a CPU utilization 
# for a specific VM is higher than 80 percent
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name  = "EC2 High CPU (${aws_instance.my_server.id})"
  namespace   = "AWS/EC2"
  metric_name = "CPUUtilization"
  # You have to create a separate alarm for each EC2 instance
  dimensions = {
    InstanceId = aws_instance.my_server.id
  }
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  period                    = "300"
  statistic                 = "Average"
  threshold                 = "80"
  alarm_description         = "This metric monitors CPU utilization for the following instance: ${aws_instance.my_server.id}. If the CPU usage exceeds 80%, you'll get an alert."
  insufficient_data_actions = []

  ok_actions    = [aws_sns_topic.alarms.arn]
  alarm_actions = [aws_sns_topic.alarms.arn]
}
