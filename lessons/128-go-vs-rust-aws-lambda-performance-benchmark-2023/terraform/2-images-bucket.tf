# Generate random id for S3 bucket.
resource "random_id" "server" {
  byte_length = 4
}

# Create an S3 bucket to store images for benchmark test.
resource "aws_s3_bucket" "images_bucket" {
  bucket        = "images-${random_id.server.hex}"
  force_destroy = true
}

# Disable all public access to the S3 bucket.
resource "aws_s3_bucket_public_access_block" "images_bucket" {
  bucket = aws_s3_bucket.images_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Upload test image to S3 bucket.
resource "aws_s3_object" "image" {
  bucket = aws_s3_bucket.images_bucket.id

  key    = "thumbnail.png"
  source = "../thumbnail.png"

  etag = filemd5("../thumbnail.png")
}
