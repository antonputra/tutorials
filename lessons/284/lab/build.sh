#!/bin/bash
# build.sh: everything the hand-built container needs, on a fresh Ubuntu 26.04 server with no Docker: missions 2 to 8
# of the lab, the clean way. Each line is one command of the hand build in the video; the lab's page types them one at
# a time, with the errors left in. This is the clean build in one go: 27 commands. The user is made before the folders
# are stacked, so nothing below a mounted stack changes afterwards.
# The 28th command starts the app: ./launch.sh. The app must already be in /app (README.md, "Run it").
set -e
F=/srv/status-files

# 1. the files the app needs: its two files, Python, the loader and four libraries, Python's own code,
#    and one small toolbox (busybox) to look around inside
sudo mkdir -p $F/app $F/data $F/proc
sudo cp /app/status.py /app/message.txt $F/app/
sudo mkdir -p $F/usr/bin
sudo cp /usr/bin/python3.14 $F/usr/bin/python3
for f in $(ldd /usr/bin/python3.14 | grep -o '/[^ ]*'); do sudo mkdir -p $F$(dirname $f) && sudo cp -L $f $F$f; done
sudo mkdir -p $F/usr/lib/python3.14
sudo cp -a /usr/lib/python3.14/. $F/usr/lib/python3.14/
sudo mkdir -p $F/bin
sudo cp /usr/bin/busybox $F/bin/
sudo chroot $F /bin/busybox --install -s /bin

# 2. the folder we keep, and the app's user, who owns it (and the image's /data, for the Docker half)
sudo mkdir /srv/status-keep
sudo useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin status
sudo chown 10001:10001 /srv/status-keep /srv/status-files/data

# 3. stacked folders: our files at the bottom, an empty folder on top, one merged folder for the app;
#    the folder we keep is mounted into the merged folder at /data
sudo mkdir -p /srv/status-1/top /srv/status-1/work /srv/status-1/merged
sudo mount -t overlay overlay -o lowerdir=/srv/status-files,upperdir=/srv/status-1/top,workdir=/srv/status-1/work /srv/status-1/merged
sudo mount --bind /srv/status-keep /srv/status-1/merged/data

# 4. its own network: a namespace, a pair of linked interfaces, one address at each end
sudo ip netns add status
sudo ip link add veth-server type veth peer name veth-app
sudo ip link set veth-app netns status
sudo ip addr add 10.0.0.1/24 dev veth-server
sudo ip link set veth-server up
sudo ip netns exec status ip addr add 10.0.0.2/24 dev veth-app
sudo ip netns exec status ip link set veth-app up
sudo ip netns exec status ip link set lo up

# 5. its limits: a control group with a memory limit and a CPU time budget
sudo mkdir /sys/fs/cgroup/status
echo 64M | sudo tee /sys/fs/cgroup/status/memory.max
echo "50000 100000" | sudo tee /sys/fs/cgroup/status/cpu.max

echo "ready: 27 commands. The 28th starts the app, in terminal 1: $(cd "$(dirname "$0")" && pwd)/launch.sh"
