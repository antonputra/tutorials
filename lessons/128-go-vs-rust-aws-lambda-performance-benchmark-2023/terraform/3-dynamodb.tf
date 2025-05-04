resource "aws_dynamodb_table" "images" {
  name           = "images"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 100
  hash_key       = "last_modified_date"

  attribute {
    name = "last_modified_date"
    type = "S"
  }
}
