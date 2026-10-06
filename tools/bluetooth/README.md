# Bluetooth Receiver test tools

Measure A2DP reception on a V3 Blaze over ADB. See [Bluetooth Receiver dropouts](../../docs/BLUETOOTH-RANGE.md) for the results these tools produced.

| File | Runs on | Purpose |
|---|---|---|
| `airtime-test.sh` | Blaze | Bind-mounts the v1.2.0 `main.conf` over official firmware in RAM and restarts `bluetoothd` and `bt-agent`. Reboot to undo. |
| `lqlog.sh` | Blaze | Logs HCI link quality and link role once per second. |
| `measure.sh` | Host | `start <name>` / `stop <name>`: records HCI with `btmon` and the link-quality log to the microSD card, then copies them to `captures/<name>/`. |
| `analyze.py` | Host | Per 10 seconds: received rate, dropped audio, discontinuities, missing RTP packets and minimum link quality. |

```bash
adb shell mkdir -p /usr/data/bt-test
adb push airtime-test.sh lqlog.sh ../../theme/v1.3/etc/bluetooth/main.conf /usr/data/bt-test/
adb shell sh /usr/data/bt-test/airtime-test.sh   # optional: test the fix on official firmware
# enter Bluetooth Receiver mode, connect the source and start playback
sh measure.sh start run1
# ... test ...
sh measure.sh stop run1
python3 analyze.py captures/run1
```

A microSD card must be mounted on the Blaze. Reboot between runs, and check the source codec rate before each run: Android restores adaptive LDAC after reconnecting. Captures contain Bluetooth addresses and encoded audio; do not publish them.
