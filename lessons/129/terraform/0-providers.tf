# Define AWS terraform provider.
provider "aws" {
  region = "us-east-1"
}

# Define Google terraform provider.
provider "google" {
  project = "devops-364717"
  region  = "us-east4"
}

# Generate a random ID to create unique resources such as S3 and GS buckets.
resource "random_id" "lesson" {
  byte_length = 4
}

# Define version constraints for used terraform providers.
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.33.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.39.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4.3"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2.0"
    }
  }

  required_version = "~> 1.0"
}
