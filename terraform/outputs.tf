output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.platform_cluster.endpoint
}

output "cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = aws_eks_cluster.platform_cluster.name
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_eks_cluster.platform_cluster.vpc_config[0].cluster_security_group_id
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.k8s_vpc.id
}

