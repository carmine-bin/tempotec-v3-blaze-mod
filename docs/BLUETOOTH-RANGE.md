# Bluetooth Receiver dropouts

In official v1.3 Bluetooth Receiver mode, the source phone could not sustain LDAC 990 kb/s even next to the V3 Blaze, and dropouts appeared at short range or in busy RF environments. The cause was host configuration, not the radio: BlueZ kept the controller scanning while it received audio. Both v1.2.0 editions change two lines of `/etc/bluetooth/main.conf`. Testing showed a substantial improvement: LDAC 990 kb/s is now sustained without dropped audio at distances that previously failed. Both release images were flashed and tested on a physical V3 Blaze.

This is separate from the [v1.3 LDAC decoder corruption](LDAC-RECEIVER-ARTIFACTS.md), where audio was damaged although every packet arrived.

## Cause

The V3 Blaze has one 2.4 GHz radio (Broadcom BCM43438A1) that time-shares everything the controller does. Official v1.3 ships BlueZ 5.54 with `ControllerMode = dual` and `FastConnectable = true`. HCI captures recorded during reception show three activities competing with the A2DP link:

| Activity | Official v1.3 parameters | Share of radio time requested |
|---|---|---|
| LE background scan | Passive, 30 ms window every 60 ms, accept-list filter | up to 50 % |
| Page scan (`FastConnectable`) | 11.25 ms interlaced every 160 ms | about 14 % |
| Inquiry scan (discoverable) | Default parameters | about 1 % |

The kernel runs the LE background scan whenever a bonded device has LE keys. Phones and laptops paired with the Blaze usually bond over both transports, so in practice the scan ran during all reception. None of it is needed: A2DP, AVRCP and HiBy Link (RFCOMM serial port) use BR/EDR.

The phone sends audio only in slots the link actually provides. With part of the radio time spent scanning, there is less room for packets and retransmissions. The source's encoder queue overflows and it discards audio before numbering RTP packets. Captures therefore show **continuous RTP sequence numbers with jumps in the RTP timestamp**: nothing is lost in the air, but the phone never sent the audio. This explains why:

- 990 kb/s failed even at close range with perfect link quality (255);
- the phone's adaptive LDAC stayed near 400 kb/s with a perfect link;
- dropouts grew quickly in crowded RF, where more retransmissions are needed.

## Correction

```diff
-ControllerMode = dual
+ControllerMode = bredr
-FastConnectable = true
+FastConnectable = false
```

`bredr` disables LE in the controller (HCI `Read LE Host Support` returns 0) and removes LE scanning and advertising. `FastConnectable = false` returns page scan to the standard 11.25 ms every 1.28 s. Every other line of the official file is unchanged. The builder regenerates the file from the official one and checks both hashes: `0ea56014…308d4` → `a29ec0f8…708a`.

Trade-offs: the Blaze no longer uses Bluetooth LE, and an incoming connection from another device can take up to about a second longer to start. No player feature that uses LE was found, and HiBy Link was confirmed working with the change. Bluetooth source mode (Blaze to headphones) uses the same configuration but was not tested.

## Measurements

One V3 Blaze, an Android phone as source with LDAC fixed at 990 kb/s, indoors. Each configuration was applied in RAM over official v1.3 and the device was rebooted between runs. The Blaze recorded HCI to its microSD card. "Dropped audio" is RTP timestamp advance beyond each packet's own duration.

Spot A: near, then moderate distance.

| Configuration | Rate at link quality 255 | Dropped audio | Lost RTP packets |
|---|---|---|---|
| Official v1.3 | about 400 kb/s | **60 %** | 0 |
| Official + no master role (diagnostic) | about 410 kb/s | 57 % | 0 |
| v1.2.0 `main.conf` | 990 kb/s | **0.1 %** | 0 |
| v1.2.0 `main.conf` + no master role | 990 kb/s | 0 % | 0 |

Spot B: about 12 m through two doors and the tester's body. With the official configuration, dropouts began before the first door.

| Configuration | Dropped audio (about 40 s at spot B) | Minimum link quality |
|---|---|---|
| v1.2.0 `main.conf` | 24 s | 49 |
| + no master role | 33 s | 37 |
| + controller sleep mode disabled | 33 s | 15 |
| + AzureWave HCD `0122.0538` | 31 s | 22 |

At spot B the remaining dropouts start when link quality falls below about 60, which is the physical limit of the link. Differences between spot B runs follow body and phone position more than configuration. [Evidence](evidence/bluetooth-receiver-airtime.json).

## Ruled out

- **Master role.** BlueZ accepts incoming connections as central because its AVDTP and AVCTP listeners request it (`bluetoothd` VA `0x411e08` and `0x421fb0`). A two-byte diagnostic patch made the Blaze peripheral; alone it changed nothing and it added nothing to the `main.conf` change. Not shipped.
- **Controller sleep mode.** Disabling it at runtime (`HCI 0xfc27`, all zero) gave no improvement. Not shipped.
- **Bluetooth patch file.** The AzureWave HCD loaded correctly (HCI 4.2, revision 538) and performed the same as the AP6212A1 HCD. Not shipped.
- **Wi-Fi.** `wlan0` was down and the Wi-Fi SDIO interrupt count did not change during tests.
- **Decoder or host CPU.** No RTP packets were missing at the HCI; the loss happened at the source.
- **Antenna.** It sits under the plastic top cover, separated from the metal frame. After the change the range is consistent with a working antenna.

## Testing it yourself

[`tools/bluetooth`](../tools/bluetooth) applies the corrected `main.conf` to unmodified firmware in RAM and records HCI and link quality to the microSD card. `analyze.py` reports rate, dropped audio and lost packets per 10 seconds. Captures contain Bluetooth addresses and audio; do not publish them.

Android restores adaptive LDAC after each reconnection. Check the codec rate before every run.
