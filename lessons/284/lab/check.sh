#!/bin/bash
# check.sh: is the hand-built container what the video shows? Run it in terminal 2 while launch.sh runs in terminal 1.
# It prints one line per check and ends with the number that failed.
fail=0
ok() { echo "ok    $1"; }
no() { echo "FAIL  $1"; fail=$((fail + 1)); }
P=$(pgrep -n -f '^python3 /app/status')
[ -n "$P" ] && ok "the app runs: process $P on the server" || { no "no app process"; echo "1 failed"; exit 1; }

page=$(curl -s -m 5 http://10.0.0.2:8000/status)
case "$page" in *"Status: OK"*) ok "the page answers at 10.0.0.2:8000" ;; *) no "no page at 10.0.0.2:8000" ;; esac
curl -s -m 2 -o /dev/null http://127.0.0.1:8000/status && no "the server's own port 8000 answers too" || ok "nothing listens on the server's own port 8000"

[ "$(sudo readlink /proc/$P/root)" = /srv/status-1/merged ] && ok "its root folder is /srv/status-1/merged" || no "its root folder is not /srv/status-1/merged"
[ "$(findmnt -n -o FSTYPE /srv/status-1/merged)" = overlay ] && ok "that folder is stacked: our files below, a top folder above" || no "that folder is not a stacked mount"
[ "$(grep NSpid /proc/$P/status | awk '{print $NF}')" = 1 ] && ok "inside, it is process 1 ($(grep NSpid /proc/$P/status | tr '\t' ' '))" || no "it is not process 1 inside"
[ "$(sudo nsenter --target $P --all --root ps | grep -c python3)" = 1 ] && ok "inside, ps lists one python3" || no "ps inside does not list exactly one python3"
[ "$(cat /proc/$P/cgroup)" = "0::/status" ] && ok "it is in the group /status" || no "it is not in the group /status"
[ "$(cat /sys/fs/cgroup/status/memory.max)" = 67108864 ] && ok "memory.max is 67108864" || no "memory.max is not 67108864"
[ "$(cat /sys/fs/cgroup/status/cpu.max)" = "50000 100000" ] && ok "cpu.max is 50000 100000" || no "cpu.max is not 50000 100000"
[ "$(grep '^Uid:' /proc/$P/status | awk '{print $2}')" = 10001 ] && ok "it runs as user 10001 (status)" || no "it does not run as user 10001"
[ "$(grep '^CapEff:' /proc/$P/status | awk '{print $2}')" = 0000000000000000 ] && ok "it has none of root's powers" || no "it still has some of root's powers"
tail -1 /srv/status-keep/requests.log | grep -q ' 10.0.0.1 GET /status$' && ok "the request is in /srv/status-keep/requests.log" || no "the request is not in /srv/status-keep/requests.log"
sudo lsns -p $P | awk '$3 <= 2 {print $2}' | sort | tr '\n' ' ' | grep -q 'mnt net pid' && ok "its own namespaces: mnt, net and pid" || no "its own namespaces are not mnt, net and pid"

echo "$fail failed"
[ "$fail" -eq 0 ]
