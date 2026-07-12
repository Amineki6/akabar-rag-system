terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1" # Frankfurt
}

# --- 1. Reuse Networking Module ---
# This creates a NEW VPC specifically for your Lab
module "networking" {
  source = "../terraform/modules/networking"
}

# --- 2. Security Group for Kubernetes ---
resource "aws_security_group" "k8s_sg" {
  name        = "k8s-lab-sg"
  description = "Allow SSH, HTTP, HTTPS, and K8s API"
  vpc_id      = module.networking.vpc_id

  # SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP (ArgoCD / App)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubernetes API (6443) - Required to connect kubectl from your laptop
  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- 3. Compute (The K8s Node) ---
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_key_pair" "k8s_key" {
  key_name   = "k8s-lab-key"
  public_key = file("~/.ssh/id_digitalocean.pub") # Reusing your existing key
}

resource "aws_instance" "k8s_node" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium" # Minimum recommended for K8s + ArgoCD
  subnet_id     = module.networking.public_subnet_id
  key_name      = aws_key_pair.k8s_key.key_name

  vpc_security_group_ids = [aws_security_group.k8s_sg.id]

  root_block_device {
    volume_size = 80 # K8s needs a bit more space
    volume_type = "gp3"
  }

  tags = { Name = "akabar-k8s-lab" }

  user_data = file("${path.module}/k3s-install.sh")
}

# --- 4. Outputs ---
output "k8s_node_ip" {
  value = aws_instance.k8s_node.public_ip
  description = "Public IP of the K8s Node"
}