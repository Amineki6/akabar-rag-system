provider "aws" {
  region = "eu-central-1"
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# --- S3 Bucket for State Storage ---
resource "aws_s3_bucket" "terraform_state" {
  bucket = "akabar-state-${random_string.bucket_suffix.result}"

  # Prevent accidental deletion of this critical bucket
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- DynamoDB Table for Locking ---
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "akabar-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

# --- Outputs to help with Phase 2 ---
output "s3_bucket_name" {
  value       = aws_s3_bucket.terraform_state.id
  description = " The name of the S3 bucket to use in the backend config"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.terraform_locks.name
  description = "The name of the DynamoDB table to use in the backend config"
}