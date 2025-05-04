output "eks_init" {
  value       = "aws eks update-kubeconfig --name ${var.eks_cluster_name} --region ${var.region}"
  description = "Run the following command to connect to the EKS cluster."
}
