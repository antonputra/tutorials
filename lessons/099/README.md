# Kubernetes Local Persistent Volume: DON'T use hostPath!

[YouTube Tutorial](https://youtu.be/fADm0DGgEJw)

## Postgress

```bash
kubectl port-forward database-postgresql-0 5432
psql --host localhost \
    --port 5432 \
    --username postgres \
    --password
CREATE DATABASE test_hostpath;
\l
```

## Drain Nodes

```bash
kubectl get nodes
kubectl drain <node-name> \
    --delete-emptydir-data \
    --ignore-daemonsets
```

## Prepare Disks

```bash
ssh -i ~/Downloads/devops.pem ec2-user@3.239.109.105
lsblk
sudo mkfs -t xfs /dev/nvme1n1
sudo lsblk -o +UUID

sudo mkdir \
-p /mnt/ssd-disks/<UUID>

sudo mount \
/dev/nvme1n1 \
/mnt/ssd-disks/<UUID>


sudo vi /etc/fstab
UUID=<UUID>  /mnt/ssd-disks/<UUID>  xfs  defaults,nofail  0  2
```
