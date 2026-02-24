# Redis vs Valkey: Performance & Comparison

You can find tutorial [here](https://youtu.be/gwtoJTevxSA).

```bash
# ec2: c8g.4xlarge -> 16/32
/usr/local/bin/redis-server --io-threads 9 --io-threads-do-reads yes --save --protected-mode no
/usr/local/bin/valkey-server --io-threads 9 --io-threads-do-reads yes --save --protected-mode no
```

## Redis

```bash
sudo apt -y install build-essential pkg-config

export REDIS_VER="8.6.0"

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

sudo useradd --system --no-create-home --shell /bin/false redis

sudo tee /etc/systemd/system/redis.service <<EOF
[Unit]
Description=Redis
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
LimitNOFILE=100000
User=redis
Group=redis
Type=simple
Restart=on-failure
RestartSec=30s
ExecStart=/usr/local/bin/redis-server --io-threads 9 --io-threads-do-reads yes --save --protected-mode no

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable redis
sudo systemctl start redis
sudo systemctl status redis
```

## Valkey

```bash
sudo apt -y install build-essential pkg-config

export VALKEY_VER="9.0.2"

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

sudo useradd --system --no-create-home --shell /bin/false valkey

sudo tee /etc/systemd/system/valkey.service <<EOF
[Unit]
Description=Valkey
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
LimitNOFILE=100000
User=valkey
Group=valkey
Type=simple
Restart=on-failure
RestartSec=30s
ExecStart=/usr/local/bin/valkey-server --io-threads 9 --io-threads-do-reads yes --save --protected-mode no

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable valkey
sudo systemctl start valkey
sudo systemctl status valkey
```
