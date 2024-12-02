# Redis vs Dragonfly Performance (Latency - Throughput - Saturation)

You can find tutorial [here](https://youtu.be/DgcBFb4L0dI).

## Install Dragonfly

```bash
export VERSION="1.25.4"

wget https://github.com/dragonflydb/dragonfly/releases/download/v${VERSION}/dragonfly_amd64.deb
sudo dpkg -i dragonfly_amd64.deb

sudo tee /etc/dragonfly/dragonfly.conf <<EOF
--pidfile=/var/run/dragonfly/dragonfly.pid
--log_dir=/var/log/dragonfly
--dir=/var/lib/dragonfly
--max_log_size=20
--cache_mode=true
--df_snapshot_format=false
EOF

sudo chown dfly:dfly /etc/dragonfly/dragonfly.conf

sudo systemctl enable dragonfly
sudo systemctl restart dragonfly
sudo systemctl status dragonfly
```

## Install Redis

```bash
sudo apt -y install build-essential pkg-config

export REDIS_VER="7.4.1"

wget https://github.com/redis/redis/archive/refs/tags/${REDIS_VER}.tar.gz
tar -xzf ${REDIS_VER}.tar.gz
sudo mv redis-${REDIS_VER}/ /opt/redis
cd /opt/redis/
make
sudo make install

cat <<EOF | sudo tee -a /etc/sysctl.conf
vm.overcommit_memory = 1
EOF

sudo sysctl vm.overcommit_memory=1

sudo tee /etc/redis.conf <<EOF
maxclients 10000
protected-mode no
appendonly no
save ""
EOF

sudo useradd --system --no-create-home --shell /bin/false redis

sudo chown redis:redis /etc/redis.conf

sudo tee /etc/systemd/system/redis.service <<EOF
[Unit]
Description=Redis
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
User=redis
Group=redis
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/redis-server /etc/redis.conf

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable redis
sudo systemctl start redis
sudo systemctl status redis
```

## Create Redis Cluster

```bash
export REDIS_VER="7.4.1"

wget https://github.com/redis/redis/archive/refs/tags/${REDIS_VER}.tar.gz
tar -xzf ${REDIS_VER}.tar.gz
sudo mv redis-${REDIS_VER}/ /opt/redis
cd /opt/redis/
make
sudo make install

cat <<EOF | sudo tee -a /etc/sysctl.conf
vm.overcommit_memory = 1
EOF

sudo sysctl vm.overcommit_memory=1

sudo tee /etc/redis.conf <<EOF
cluster-enabled yes
cluster-config-file /etc/redis/nodes.conf
cluster-node-timeout 5000

dir /etc/redis/
maxclients 10000
protected-mode no
appendonly no
save ""
EOF

sudo useradd --system --no-create-home --shell /bin/false redis

sudo mkdir /etc/redis
sudo chown -R redis:redis /etc/redis
sudo chown redis:redis /etc/redis.conf

sudo tee /etc/systemd/system/redis.service <<EOF
[Unit]
Description=Redis
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
User=redis
Group=redis
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/redis-server /etc/redis.conf

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable redis
sudo systemctl start redis
sudo systemctl status redis

redis-cli --cluster create redis-0.antonputra.pvt:6379 redis-1.antonputra.pvt:6379 redis-2.antonputra.pvt:6379 redis-3.antonputra.pvt:6379 --cluster-replicas 0
```
