output "cluster_security_group_id" {
  description = "Cluster security group that was created by Amazon EKS for the cluster."
  value       = aws_eks_cluster.eks.vpc_config[0].cluster_security_group_id
}
