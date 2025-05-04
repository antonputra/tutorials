# Create an S3 bucket to store lambda source code (zip archives)
resource "aws_s3_bucket" "functions" {
  bucket        = "functions-${random_id.lesson.hex}"
  force_destroy = true
}

# Disable all public access to the S3 bucket
resource "aws_s3_bucket_public_access_block" "functions" {
  bucket = aws_s3_bucket.functions.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Create an S3 bucket to store images for benchmark test.
resource "aws_s3_bucket" "images" {
  bucket        = "images-${random_id.lesson.hex}"
  force_destroy = true
}

# Disable all public access to the S3 bucket.
resource "aws_s3_bucket_public_access_block" "images" {
  bucket = aws_s3_bucket.images.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Upload test image to S3 bucket.
resource "aws_s3_object" "image" {
  bucket = aws_s3_bucket.images.id

  key    = "yosemite.jpg"
  source = "../yosemite.jpg"

  etag = filemd5("../yosemite.jpg")
}
