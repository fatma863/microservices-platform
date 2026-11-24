variable "aws_region" {
  type        = string
  description = "AWS region for cluster deployment"
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "production"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block"
  default     = "10.0.0.0/16"
}

variable "cluster_name" {
  type        = string
  description = "Name of the EKS Cluster"
  default     = "cloud-microservices-eks"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for EKS worker nodes"
  default     = "t3.medium"
}

