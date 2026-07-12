# modules/compute/main.tf

# --- Variables (Inputs from the Root) ---
variable "vpc_id" {}
variable "subnet_id" {}
variable "public_key_path" {
  default = "~/.ssh/id_digitalocean.pub"
}

# --- Resources ---
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] 
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_security_group" "web_sg" {
  name        = "web-security-group"
  description = "Allow SSH, HTTP, HTTPS"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
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

resource "aws_key_pair" "deployer" {
  key_name   = "deployer-key"
  public_key = file(var.public_key_path)
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  subnet_id     = var.subnet_id
  key_name      = aws_key_pair.deployer.key_name
  
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  availability_zone      = "eu-central-1a"

  root_block_device {
    volume_size = 80    
    volume_type = "gp3"
  }

  tags = { Name = "akabar-production" }

  user_data = file("${path.root}/scripts/setup.sh")
}

resource "aws_ebs_volume" "mongo_data" {
  availability_zone = "eu-central-1a"
  size              = 10
  type              = "gp3"
  tags = { Name = "akabar-mongo-data" }
}

resource "aws_volume_attachment" "ebs_att" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.mongo_data.id
  instance_id = aws_instance.web.id
}

resource "aws_eip" "lb" {
  instance = aws_instance.web.id
  domain   = "vpc"
}

# --- Outputs ---
output "server_ip" {
  value = aws_eip.lb.public_ip
}