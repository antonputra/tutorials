#!/bin/bash
# launch.sh: the 28th command. It starts the app inside everything build.sh prepared. Read it from the right:
#   python3 /app/status.py --listen 0.0.0.0   the app, listening on every address of its own network
#   --setuid 10001 --setgid 10001             as the user status, with none of root's powers
#   --root=/srv/status-1/merged               with the merged folder as its whole file tree
#   --pid --fork --mount-proc                 with its own list of processes (it is process 1 there)
#   ip netns exec status                      in its own network
#   echo $$ > .../status/cgroup.procs         in the group with the 64 MB and CPU limits
# It stays in the foreground; stop it from another terminal with: sudo kill -KILL <its PID on the server>
# (a plain "kill" does nothing: the app is process 1 of its namespace and never asked to get that signal).
sudo sh -c 'echo $$ > /sys/fs/cgroup/status/cgroup.procs && exec ip netns exec status unshare --pid --fork --mount-proc --root=/srv/status-1/merged --setuid 10001 --setgid 10001 python3 /app/status.py --listen 0.0.0.0'
