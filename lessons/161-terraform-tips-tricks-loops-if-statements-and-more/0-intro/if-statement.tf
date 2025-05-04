module "cluster_autoscaler" {
  source = "../../../infrastructure-modules/kubernetes-addons"

  if env == "prodcution" {
    env         = "production"
    eks_name    = "demo"
    helm_verion = "9.28.0"      
  }
}
