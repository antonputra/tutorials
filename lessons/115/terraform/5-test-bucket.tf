resource "random_pet" "test_bucket_name" {
  prefix = "test"
  length = 2
}

resource "aws_s3_bucket" "test" {
  bucket        = random_pet.test_bucket_name.id
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "test" {
  bucket = aws_s3_bucket.test.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "test" {
  bucket = aws_s3_bucket.test.id

  key     = "hello.json"
  content = jsonencode({ name = "S3" })
}

output "test_s3_bucket" {
  value = random_pet.test_bucket_name.id
}
