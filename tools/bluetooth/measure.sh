#!/bin/sh
# Run on the host with the V3 Blaze attached over ADB and a microSD card mounted.
#   sh measure.sh start <name>   start HCI capture and link-quality log on the card
#   sh measure.sh stop  <name>   stop and copy to ./captures/<name>/
# Captures contain Bluetooth addresses and encoded audio; do not publish them.
SD=/usr/data/mnt/sd_0/bt-test
case "$1" in
start)
    adb shell "mkdir -p $SD/$2; setsid btmon -w $SD/$2/seg1.btsnoop </dev/null >/dev/null 2>&1 & setsid sh /usr/data/bt-test/lqlog.sh $SD/$2/lq.log </dev/null >/dev/null 2>&1 & sleep 1"
    adb shell "ps | grep -E 'btmon|lqlog' | grep -v grep"
    ;;
stop)
    adb shell "killall btmon; kill \$(cat /tmp/lqlog.pid) 2>/dev/null; sleep 0.5"
    mkdir -p "captures/$2"
    adb pull "$SD/$2/." "captures/$2/" >/dev/null && echo "captures/$2"
    ;;
*) echo "Usage: $0 {start|stop} <name>"; exit 1 ;;
esac
