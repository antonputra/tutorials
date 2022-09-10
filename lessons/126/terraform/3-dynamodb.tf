# Create DynamoDB table
resource "aws_dynamodb_table" "meta" {
  name           = "Meta"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 1000
  hash_key       = "LastModified"

  attribute {
    name = "LastModified"
    type = "S"
  }
}
