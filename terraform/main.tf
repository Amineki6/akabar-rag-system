terraform {
  backend "s3" {
    bucket         = "akabar-state-xv4g5np3"
    key            = "global/s3/terraform.tfstate"
    region         = "eu-central-1" # Frankfurt
    dynamodb_table = "akabar-terraform-locks"
    encrypt        = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

# --- CALL MODULES ---

module "networking" {
  source = "./modules/networking"
}

module "compute" {
  source = "./modules/compute"

  # We pass data FROM networking TO compute here
  vpc_id    = module.networking.vpc_id
  subnet_id = module.networking.public_subnet_id
}

# --- FINAL OUTPUTS ---
output "production_ip" {
  value = module.compute.server_ip
}