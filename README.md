# TempoTec V3 Blaze firmware

Official TempoTec v1.3 (`V3_ANALOG_2025`) with corrections for Bluetooth Receiver dropouts and LDAC audio artifacts. Project version: v1.2.1.

<p align="center"><img src="docs/img/blaze-full-mod.jpg" alt="TempoTec V3 Blaze running Full Mod" width="70%"></p>

[Español](README.es.md) · [Downloads](https://github.com/carmine-bin/tempotec-v3-blaze-mod/releases) · [Install](docs/INSTALL.md) · [Recovery](docs/RECOVERY.md) · [Build](docs/BUILD.md) · [Telegram](https://t.me/V3_Blaze_Discussion)

## Editions

| Edition | Contents | Filename |
|---|---|---|
| V3 Blaze v1.3 Stock + Fixes | Official appearance and features, with only the Bluetooth Receiver corrections | `V3-Blaze-v1.3-Stock-Fixes-v1.2.0.upt` |
| V3 Blaze v1.3 Full Mod | Corrected v1.3 base, customized HiBy-style interface and tested UI fixes | `V3-Blaze-v1.3-Full-Mod-v1.2.1.upt` |

Both editions use the official kernel and include v1.3 PEQ, real-time Bluetooth search and stability improvements. Both include the same two Bluetooth Receiver corrections:

- **Dropouts:** BlueZ kept the radio scanning while receiving audio, so the source could not sustain LDAC 990 kb/s even at close range. Two lines of `/etc/bluetooth/main.conf` stop the scanning; 990 kb/s now plays without dropped audio at distances that previously failed. [Details and measurements](docs/BLUETOOTH-RANGE.md).
- **LDAC artifacts:** a one-byte decoder correction removes the digital artifacts introduced by official v1.3. [Decoder evidence](docs/LDAC-RECEIVER-ARTIFACTS.md).

Stock + LDAC Fix is now called Stock + Fixes. Stock + Fixes is unchanged in v1.2.1.

Full Mod includes everything in Stock + Fixes, plus:

**Interface**

- HiBy OS-style launcher, categories, dark interface and fullscreen Now Playing.
- Battery icon: the fill no longer vanishes below about 30 % and there is no doubled battery while charging; below 16 % the frame turns red and the level stays visible in the theme color; solid frame corners.
- Low-battery notice shows its message instead of an empty grey card.
- Gain icons with all three levels.
- Working brightness slider in the pull-down. Its volume controls are hidden; volume remains available elsewhere.
- Accent tinting corrected: colour swatches and QR codes are left alone.
- TempoTec logos and branding restored; missing interface elements restored.
- Launcher backgrounds, play/pause images and popup text corrected; native Balance icon in Quick Settings with the modern tile style.

**Navigation and screens**

- Opening an album is fast again: the official v1.3 music list is used.
- Long-press Power shutdown countdown restored.
- The shutdown screen covers the whole display when opened from Now Playing.
- Correct headers on pages opened from the Now Playing menu.
- Changing the theme color returns to the main screen instead of Music → Songs.
- Settings cards no longer corrupt when the scrollbar disappears.
- Now Playing no longer shows the next track's audio quality instead of the current one.

**Settings**

- Settings → About (the route to developer mode and ADB) and Settings → Theme color.
- TF-card image and database cache.
- The DAC setting is remembered across restarts.

**System**

- MMC read-ahead of 2048 and VFS cache pressure of 50, applied only where the paths exist.
- Internal storage mounted with `noatime` instead of `sync`.

These tweaks are described in the [technical notes](docs/HOW-IT-WORKS.md); their performance impact has not been benchmarked.

**Kept from official v1.3:** PEQ, real-time Bluetooth search, TempoTec's stability fixes, the official kernel and the same microSD installation.

**Known limitation:** the pull-down menu's battery icon keeps its white frame at low charge.

The interface was adapted through Kae0's V3 Analog port of HiBy artwork. See [credits](CREDITS.md), [changelog](CHANGELOG.md) and [UI fix details](docs/UI-FIXES.md).

## Known limitations

When the album-art screensaver is active, track information and artwork may take about 1.5 seconds to update after a track change. The same behavior was reproduced on official TempoTec v1.2 and v1.3 firmware.

The Blaze no longer uses Bluetooth LE. No player feature that needs it was found; A2DP, AVRCP and HiBy Link use classic Bluetooth. Beyond about 12 m with walls in between, LDAC 990 kb/s still drops out and the source lowers its rate; this is the physical limit of the link. [Bluetooth Receiver details](docs/BLUETOOTH-RANGE.md).

Firmware v1.3 contains an additional downstream coefficient-suppression rule that was not found in the public sources examined. Bypassing that rule corrected the Bluetooth Receiver LDAC audio corruption on physical V3 Blaze hardware. Its author and purpose are unknown. [Decoder evidence](docs/LDAC-RECEIVER-ARTIFACTS.md).

## Install

Only for TempoTec V3 Blaze (`V3_ANALOG_2025`), not the older V3 Analog. Flashing carries risk; read [recovery instructions](docs/RECOVERY.md) first.

**A file named `update.upt` takes priority over `v3_analog_2025.upt`, even when updating from Settings. Remove or rename any `update.upt` before installing.**

1. **If there is a `v3_analog_2025.upt` in the root of the microSD card (for example, the one left by the OTA update), rename it to `v3_analog_2025.upt.stock` before copying the mod. Otherwise the mod will overwrite it and you will lose your copy of the official firmware.**
2. Choose an edition and verify its SHA-256 against the [v1.2.1 manifest](docs/releases/v1.2.1-manifest.json).
3. Rename it to `v3_analog_2025.upt` and copy it to the root of a microSD card.
4. Select Settings → Firmware update → Update via micro SD card. Wait for flashing and reboot to finish.

Keep backup firmware under `.upt.stock` or `.upt.bak`. See [getting the official v1.3 firmware](docs/INSTALL.md#getting-the-official-v13-firmware) and [backup and restore](docs/INSTALL.md#backup-and-restore).

Developer mode and ADB are off by default in both editions and work as in the official firmware: tap About 10 times to enable them. In the official interface and in Stock + Fixes, About is in the home menu. Full Mod's HiBy-style launcher has no About entry, so Full Mod shows About in Settings instead (the official settings configuration hides that entry because the home menu already has it). This project does not enable ADB or change how developer mode works.

Both packages are 44,367,872 bytes.

| Edition | SHA-256 | MD5 |
|---|---|---|
| Stock + Fixes | `5ce109414e739546ed19d5cc74ad9b92e5a58f8545d5d3a482f673934a5929af` | `4e9408a7415b66fdad7d0ad560103194` |
| Full Mod | `db91cf52c3ac0f0005d90563bc1fa7f9e3e85abdb2c5ce3fe2e9100c18e6695a` | `d553a52f4fe924e1f663c0e3ac1ff992` |

## Development and licence

See [build instructions](docs/BUILD.md) to build either edition and check its contents. [CONTRIBUTING.md](CONTRIBUTING.md) covers device testing.

Questions, help and bug reports: [Telegram group](https://t.me/V3_Blaze_Discussion). Confirmed, reproducible bugs go to [GitHub issues](https://github.com/carmine-bin/tempotec-v3-blaze-mod/issues) so they are tracked.

Development and reverse-engineering work was assisted by AI tools. All released firmware changes were reviewed and tested on physical V3 Blaze hardware.

The MIT licence covers original tooling and documentation. Firmware, imported artwork and LDAC code retain their respective rights holders. See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE). Not affiliated with TempoTec or HiBy.
