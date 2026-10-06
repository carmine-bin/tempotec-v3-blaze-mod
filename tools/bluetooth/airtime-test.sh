#!/bin/sh
# Test the v1.2.0 Bluetooth configuration on unmodified firmware, in RAM only.
# A reboot restores the official configuration.
#
#   adb shell mkdir -p /usr/data/bt-test
#   adb push airtime-test.sh lqlog.sh main.conf /usr/data/bt-test/
#   adb shell sh /usr/data/bt-test/airtime-test.sh
#
# main.conf must be the patched file from theme/v1.3/etc/bluetooth/main.conf.
# Afterwards enter Bluetooth Receiver mode and connect the source.
D=/usr/data/bt-test
CONF=/etc/bluetooth/main.conf

if grep -q " $CONF " /proc/mounts; then
    echo "Already mounted; reboot before testing again."
    exit 1
fi
grep -q '^ControllerMode = bredr$' "$D/main.conf" || { echo "Wrong main.conf"; exit 1; }
mount -o bind "$D/main.conf" "$CONF" || exit 1

# bluetoothd reads main.conf only at startup. The agent registered with the
# previous instance is lost; without an agent the A2DP channel is refused.
killall bluetoothd bt-agent 2>/dev/null
sleep 1
setsid /usr/libexec/bluetooth/bluetoothd -E -C </dev/null >/dev/null 2>&1 &
sleep 2
bt-adapter --set "Powered" "On"
bt-adapter --set "Discoverable" "On"
setsid bt-agent -c NoInputNoOutput </dev/null >/dev/null 2>&1 &
sleep 1
grep -E '^(ControllerMode|FastConnectable)' "$CONF"
echo "LE Host Supported (expect 00 00):"
hcitool cmd 0x03 0x006c | tail -1
