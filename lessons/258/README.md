# Redis vs Valkey performance

You can find tutorial [here](https://youtu.be/9hDvWVJtljE).


## Redis

```bash
export REDIS_VER="8.0-rc1"

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
LimitNOFILE=100000
User=redis
Group=redis
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/redis-server /etc/redis.conf --port 6379

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable redis
sudo systemctl start redis
sudo systemctl status redis
```

## Valkey

```bash
export VALKEY_VER="8.1.1"

wget https://github.com/valkey-io/valkey/archive/refs/tags/${VALKEY_VER}.tar.gz
tar -xzf ${VALKEY_VER}.tar.gz
sudo mv valkey-${VALKEY_VER}/ /opt/valkey
cd /opt/valkey/
make
sudo make install

cat <<EOF | sudo tee -a /etc/sysctl.conf
vm.overcommit_memory = 1
EOF

sudo sysctl vm.overcommit_memory=1

sudo tee /etc/valkey.conf <<EOF
maxclients 10000
protected-mode no
appendonly no
save ""
EOF

sudo useradd --system --no-create-home --shell /bin/false valkey

sudo chown valkey:valkey /etc/valkey.conf

sudo tee /etc/systemd/system/valkey.service <<EOF
[Unit]
Description=Valkey
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
LimitNOFILE=100000
User=valkey
Group=valkey
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/valkey-server /etc/valkey.conf --port 6379

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable valkey
sudo systemctl start valkey
sudo systemctl status valkey
```