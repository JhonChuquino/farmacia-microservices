terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 🔹 VPC por defecto
data "aws_vpc" "default" {
  default = true
}

# 🔹 Subnets de la VPC por defecto
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# 🔹 AMI Ubuntu 22.04 LTS
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# 🔐 Security Group
resource "aws_security_group" "farm_sg" {
  name        = "farmacia-sg-v1"
  description = "Allow SSH, microservices and MongoDB"
  vpc_id      = data.aws_vpc.default.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.open_to_world ? "0.0.0.0/0" : var.my_ip_cidr]
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubernetes NodePort
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }





  tags = {
    Name = "farmacia-final-sg"
  }
}

# EC2 con Ubuntu + Docker Compose + microservicios
resource "aws_instance" "farmacia_api" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  vpc_security_group_ids      = [aws_security_group.farm_sg.id]
  associate_public_ip_address = true

  user_data = <<-EOF
#!/bin/bash
set -eux
export DEBIAN_FRONTEND=noninteractive

# 🔧 Actualizar e instalar dependencias
apt-get update -y
apt-get install -y python3-pip docker.io git curl

# 🧩 Instalar Docker Compose manualmente
curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-Linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 🔐 Configurar Docker
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# ⏳ Esperar a que Docker esté listo
until docker info >/dev/null 2>&1; do
  echo "Esperando a que Docker arranque..."
  sleep 5
done

# 📦 Clonar el repositorio (poner aquí la URL real)
cd /home/ubuntu
git clone "https://github.com/JhonChuquino/farmacia-microservices.git" farmacia-microservices
cd farmacia-microservices

# 🗃️ Crear volumen persistente para MongoDB
mkdir -p data/db
chmod -R 777 data/db

# 🚀 Levantar los microservicios
/usr/local/bin/docker-compose up -d --build

# 🔑 Ajustar permisos para usuario ubuntu
chown -R ubuntu:ubuntu /home/ubuntu/farmacia-microservices
EOF


  tags = {
    Name = "farmacia_api"
  }
}
