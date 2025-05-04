# Create GS bucket to store google functions source code (zip archives)
resource "google_storage_bucket" "functions" {
  name                        = "functions-${random_id.lesson.hex}"
  location                    = "US-EAST4"
  force_destroy               = true
  uniform_bucket_level_access = true
}

# Create GS bucket to store images for benchmark test.
resource "google_storage_bucket" "images" {
  name                        = "images-${random_id.lesson.hex}"
  location                    = "US-EAST4"
  force_destroy               = true
  uniform_bucket_level_access = true
}

# # Upload test image to GS bucket.
resource "google_storage_bucket_object" "image" {
  bucket = google_storage_bucket.images.name
  name   = "yosemite.jpg"
  source = "../yosemite.jpg"
}
