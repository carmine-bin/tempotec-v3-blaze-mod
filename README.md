<h1 align="center">V3 Blaze — v1.3 Firmware</h1>

<p align="center"><b>Official TempoTec v1.3, with a confirmed LDAC decoder correction. Two editions.</b><br>Stock appearance or the complete HiBy-style UI port. Both hardware-tested.</p>

<p align="center">
<img alt="Device" src="https://img.shields.io/badge/device-TempoTec%20V3%20Blaze-lightgrey">
<img alt="Base firmware" src="https://img.shields.io/badge/base-V3__ANALOG__2025%20v1.3-blue">
<img alt="Install" src="https://img.shields.io/badge/install-microSD%2C%20no%20PC-brightgreen">
<img alt="Docs" src="https://img.shields.io/badge/docs-EN%20%2B%20ES-informational">
</p>

<p align="center"><img src="docs/img/launcher.jpg" alt="Full Mod launcher" width="45%"> &nbsp; <img src="docs/img/nowplaying.jpg" alt="Full Mod Now Playing" width="45%"></p>

[Español](README.es.md) · [Install](docs/INSTALL.md) · [Recovery](docs/RECOVERY.md) · [Technical notes](docs/HOW-IT-WORKS.md) · [Build](docs/BUILD.md)

Current generation: official `V3_ANALOG_2025` **v1.3**. Project release/tag: **v1.1.0**. Project version and TempoTec base version are separate. Screenshots preserve the previous Full Mod's visual identity; they are not a new v1.3 screen-by-screen test record.

## Two downloads

**Stock + LDAC Fix** — `V3-Blaze-v1.3-Stock-LDAC-Fix.upt`: official TempoTec v1.3 appearance and features, including PEQ and TempoTec's stability fixes, plus this project's hardware-confirmed correction for v1.3 LDAC digital corruption. Hardware-tested release image; no custom theme, launcher, cache/I/O tuning or custom player patch.

**Full Mod** — `V3-Blaze-v1.3-Full-Mod.upt`: the same corrected v1.3 base, plus the complete current HiBy-style UI port and validated V3 Blaze customizations. The final hardware-tested Full Mod image, including its final launcher, play/pause and popup-text corrections.

Download either edition from [v1.1.0 Releases](https://github.com/carmine-bin/tempotec-v3-blaze-mod/releases/tag/v1.1.0). Reproductions are validated separately and do not replace the tested release images.

| Feature | Stock + LDAC Fix | Full Mod |
|---|---|---|
| Official TempoTec v1.3 base | Yes | Yes |
| Parametric EQ | Yes | Yes |
| Real-time Bluetooth search | Yes | Yes |
| v1.3 stability/reboot fixes | Yes | Yes |
| LDAC v1.3 decoder regression fix | Yes | Yes |
| Stock TempoTec UI | Yes | No |
| Current HiBy-style UI | No | Yes |
| Custom battery/UI fixes | No | Yes |
| Brightness + volume controls | Stock behavior | Custom brightness; volume UI retained; pull-down volume hidden |
| Cache/database optimizations | No | Yes |
| Relocated custom player patch | No | Yes |

## What official v1.3 adds

TempoTec's changelog adds **Parametric EQ**, **real-time Bluetooth search**, fixes an aging/freezing/crash issue and other bugs. Both editions preserve these official features. Full Mod keeps the official PEQ/filter layouts unchanged alongside the custom interface.

Previously observed v1.2 freezes/reboots improved with the official v1.3 base. In a reproduced severe Bluetooth degradation case, deliberately losing connectivity no longer rebooted the player: it stayed powered on and recovered when connectivity returned. The previously observed artwork/cover-related instability was also reported resolved. The exact JPEG encoding condition, image dimensions and filesize of that historical trigger could not be established from the retained evidence; progressive versus non-progressive JPEG remains unknown.

These stability improvements belong to **official v1.3**, not the project's LDAC patch. Official v1.3 also introduced a separate decoder regression: electronic/digital LDAC corruption despite successful packet reception. Hardware testing isolated the decoder; the correction bypasses only its problematic downstream coefficient-suppression gate. [Technical evidence](docs/LDAC-REGRESSION.md).

## Full Mod customizations

The HiBy design reached this project through **Kae0's V3 Analog port**, with the current HiBy-style launcher, category artwork, dark styling and edge-to-edge album covers. Full Mod selectively ports these changes onto v1.3 rather than overlaying an old system.

| Customization | What was corrected or retained |
|---|---|
| Battery fill | The engine crops the percentage of the fill image rather than scaling it. The donor full-battery asset put its outline/cap inside the frame. Separate bare fill and frame correct this. |
| Charging screen | The same fill/frame defect was corrected there. |
| Three-state gain | The Blaze has three levels; missing middle-state artwork was restored. |
| Brightness | Correct element name `pull_down_menu_pb` restores the binary's callback. |
| Volume | Volume UI remains available. The tested pull-down retains volume objects hidden; the old README's claim of two visible sliders was inaccurate. |
| Layouts | Missing binary-required name/type/parent elements restored, with v1.3 loading, date/clock, track-info and dialog compatibility. |
| Final visual corrections | Custom launcher fallback colors, correct play/pause artwork states and restored popup message text. |
| Tint/no-skin | Accent inclusion/exclusion corrected; colour swatches and QR artwork protected. |
| Branding | Appropriate TempoTec artwork replaces donor branding/QR assets. |
| About/developer and colour theme | About and accent-picker flags enabled; About provides the developer/ADB route. |
| Cache/database | TF image/database caching and DAC-setting persistence enabled. |
| Filesystem/I/O | Guarded MMC read-ahead `2048`, cache pressure `50`; UBIFS `sync → noatime`, which also removes synchronous writes. |
| Player patch | Independently relocated for v1.3 to file offset `0x38240` (VA `0x438240`): `08 da 10 0c → 00 00 00 00`. Omits next-track metadata parsing into the shared current-track buffer, retaining output copy and delay slot. |

The [complete manifest](build/v1.3/full-mod-manifest.json) lists 607 changed/added regular files and two added directories. The [migration notes](docs/HOW-IT-WORKS.md#migration-to-official-v13) explain patch validation. The kernel, Bluetooth/audio components and unrelated system files stay official v1.3. The final Full Mod image was validated on physical V3 Blaze hardware; that does not establish a measured benefit for every tuning option.

## Known issues and limitations

> **Known issue: Bluetooth range/interference remains under investigation. High-bandwidth LDAC modes are unreliable, and even lower LDAC rates can suffer in crowded RF environments. AAC remains stable in the same normal-use scenarios. This is separate from the fixed v1.3 LDAC decoder corruption.**

[Bluetooth range investigation](docs/BLUETOOTH-RANGE.md): Wi-Fi range also appears poor; cause unknown. Antenna, RF path/configuration, coexistence, sensitivity and hardware/firmware problems remain hypotheses.

Full Mod retains the static battery frame (no red low-battery frame), hidden heart/play-mode pull-down controls, and a brightness-only pull-down; play-mode controls remain in Now Playing. Both editions are hardware-tested, but neither solves every device problem.

## Install

> [!WARNING]
> Firmware flashing can leave the device unusable. Read [RECOVERY.md](docs/RECOVERY.md) first. **Only for TempoTec V3 Blaze (`V3_ANALOG_2025`), not the older V3 Analog.**

1. Choose one edition and verify its SHA-256 against the table or `SHA256SUMS`.
2. **Rename the selected download to exactly `v3_analog_2025.upt`.** Copy it to the root of a microSD card.
3. Use *Settings → Firmware update → Update via micro SD card*. Let recovery flash and reboot; do not interrupt it.

**Never keep a spare named `update.upt`**: recovery prioritizes it over `v3_analog_2025.upt`, including system-menu updates. Keep spares under `.upt.stock` or `.upt.bak`. Both editions use the same verified [installation](docs/INSTALL.md) and [recovery](docs/RECOVERY.md) mechanism.

| Edition | SHA-256 | MD5 |
|---|---|---|
| Stock + LDAC Fix | `273f56607d477d44bd071c1a3e2097361610c2e403cfddc7ccf51b98a56210d1` | `cd380b93df9a600a5d24cb64585aac88` |
| Full Mod | `fbb6f356cea7cae73b7af39ade9d32e0e4b0f9fc1eaab4a6ac401f6e92a4c933` | `c09b37baa6fd6a5660e4bbc355bae33c` |

## Reproduce and inspect

[BUILD.md](docs/BUILD.md) documents separate `stock-fix` and `full-mod` builds from checksum-verified official v1.3. Both verify exact binary patches, ownership/modes/links, filesystem diffs, kernel integrity and OTA checksums. A newly built image is a reproduction, not the already hardware-tested release artifact.

[Changelog](CHANGELOG.md) · [LDAC regression](docs/LDAC-REGRESSION.md) · [Range issue](docs/BLUETOOTH-RANGE.md) · [Historical v1.2 README](docs/releases/v1.0.0-README.md)

## Credits and licence

TempoTec firmware remains TempoTec's; HiBy visual assets remain HiBy's. Kae0, losber and tooling contributors retain attribution in [CREDITS.md](CREDITS.md). The existing MIT licence covers project tooling/documentation, not proprietary firmware, HiBy artwork or LDAC code. See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).

Not affiliated with or endorsed by TempoTec or HiBy.
