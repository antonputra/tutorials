# AWS EKS Kubernetes Tutorial

You can find tutorial [here](https://youtube.com/playlist?list=PLiMWaCMwGJXnKY6XmeifEpjIfkWRo9v2l&si=wc6LIC5V2tD-Tzwl).

## Changes from EKS 1.29 to 1.30

- AWS Load Balancer controller now requires `vpcId`.
- There is no longer a default storage class in EKS, so you need to explicitly set `storageClassName: gp2`.
- Updated all EKS add-ons and Helm chart versions used in this tutorial.

## Clean Up

- Manually delete IAM user secret keys from the AWS Console.
- `terraform destroy --target helm_release.external_nginx`
- `terraform destroy`
