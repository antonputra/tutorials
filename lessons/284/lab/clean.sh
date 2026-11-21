#!/bin/bash
# clean.sh: takes the hand-built container apart again. Seven commands; nothing does this for us.
P=$(pgrep -n -f '^python3 /app/status'); [ -n "$P" ] && sudo kill -KILL "$P" && sleep 1
sudo umount /srv/status-1/merged/data
sudo umount /srv/status-1/merged
sudo ip netns del status
sudo rmdir /sys/fs/cgroup/status
sudo rm -rf /srv/status-files /srv/status-1 /srv/status-keep
sudo userdel status
