#!/bin/sh
# Usage: lqlog.sh <file>. Once per second: epoch, HCI link quality, link role.
echo $$ > /tmp/lqlog.pid
while true; do
    A=$(hcitool con | awk '/ACL/{print $3}' | head -1)
    Q=$(hcitool lq "$A" 2>/dev/null | awk '{print $3}')
    R=$(hcitool con | grep -o 'lm [A-Z]*')
    echo "$(date +%s) ${Q:--} $R" >> "$1"
    sleep 1
done
