variable "aws_region" {
  description = "Región AWS"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  default     = "t2.micro"
}

variable "key_name" {
  description = "nube"
  default     = "nube"
}

variable "repo_url" {
  description = "URL del repositorio GitHub con el proyecto (docker-compose.yml)"
  default = "https://github.com/JhonChuquino/Calidad.git"
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