variable "aws_region" {
  description = "Región AWS"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  default     = "t3.micro"
}

variable "key_name" {
  description = "jhon"
  default     = "jhon"
}

variable "repo_url" {
  description = "URL del repositorio GitHub con el proyecto (docker-compose.yml)"
  default = "https://github.com/JhonChuquino/farmacia-microservices.git"
}

variable "open_to_world" {
  description = "Permitir acceso público (true para pruebas)"
  type        = bool
  default     = true
}

variable "my_ip_cidr" {
  description = "Tu IP pública para SSH y MongoDB (recomendado restringir)"
  default     = "0.0.0.0/0"
}