#!/bin/sh

killall    hiby_player    &>/dev/null
killall -9 hiby_player    &>/dev/null

if [ -f "/usr/bin/batd" ]; then
killall    batd    &>/dev/null
killall -9 batd    &>/dev/null
/usr/bin/batd -v -s -t5 -o /mnt/sd_0/batlog.txt &
fi

# tuning de I/O (ver rom-build/build-upt-v3.sh, paso 2c)
[ -w /sys/block/mmcblk0/queue/read_ahead_kb ] && echo 2048 > /sys/block/mmcblk0/queue/read_ahead_kb
[ -w /proc/sys/vm/vfs_cache_pressure ] && echo 50 > /proc/sys/vm/vfs_cache_pressure

#/usr/bin/hiby_player &>/dev/null
/usr/bin/hiby_player
sleep 1
reboot