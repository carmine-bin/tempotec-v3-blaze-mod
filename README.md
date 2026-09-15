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

Current generation: official `V3_ANALOG_2025` **v1.3**. Project release/tag: **v1.1.1**. Project version and TempoTec base version are separate. Screenshots preserve the previous Full Mod's visual identity; they are not a new v1.3 screen-by-screen test record.

## Two downloads

**Stock + LDAC Fix** — `V3-Blaze-v1.3-Stock-LDAC-Fix.upt`: official TempoTec v1.3 appearance and features, including PEQ and TempoTec's stability fixes, plus this project's hardware-confirmed correction for v1.3 LDAC digital corruption. Hardware-tested release image; no custom theme, launcher, cache/I/O tuning or custom player patch.

**Full Mod** — `V3-Blaze-v1.3-Full-Mod-v1.1.1.upt`: the same corrected v1.3 base, plus the complete current HiBy-style UI port and validated V3 Blaze customizations. The v1.1.1 Full Mod bug-fix image restores instant album opening, restores the Power-button shutdown countdown, and uses the corrected Balance Quick Settings artwork.

Download either edition from [v1.1.1 Releases](https://github.com/carmine-bin/tempotec-v3-blaze-mod/releases/tag/v1.1.1). Reproductions are validated separately and do not replace the tested release images.

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

The [complete manifest](build/v1.3/full-mod-manifest.json) lists 609 changed/added regular files and two added directories. The [migration notes](docs/HOW-IT-WORKS.md#migration-to-official-v13) explain patch validation. The kernel, Bluetooth/audio components and unrelated system files stay official v1.3. The final Full Mod image was validated on physical V3 Blaze hardware; that does not establish a measured benefit for every tuning option.

## Upstream / device limitations

The following behaviors are also present in official firmware or appear to be device-level limitations; they are not introduced by Full Mod.

- **Album-art screensaver update delay:** When the album-art screensaver is active, current-track information and artwork may take about 1.5 seconds to update after a track change. The same behavior was reproduced on official TempoTec v1.2 and v1.3 firmware, so it is not a Full Mod regression. Changing `tf_image_cache_enable` did not eliminate the delay.
- **Bluetooth RF/link margin:** Bluetooth reception has limited link margin, particularly with sustained high-bitrate LDAC and in congested RF environments. Lower-rate LDAC can also become unstable under difficult conditions, while AAC has been substantially more reliable in the observed normal-use scenarios. This behavior is separate from the v1.3 LDAC decoder corruption corrected by this project. The exact RF-level cause has not been established.

[Bluetooth range investigation](docs/BLUETOOTH-RANGE.md) contains the detailed observations.

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
| Full Mod | `c16796fe1bf24317678232bac1978df9410c62328f3327ff7ff3d1e5814adc3c` | `8cac8713dc613665c078eaa25e14aeb9` |

## Reproduce and inspect

[BUILD.md](docs/BUILD.md) documents separate `stock-fix` and `full-mod` builds from checksum-verified official v1.3. Both verify exact binary patches, ownership/modes/links, filesystem diffs, kernel integrity and OTA checksums. A newly built image is a reproduction, not the already hardware-tested release artifact.

[Changelog](CHANGELOG.md) · [LDAC regression](docs/LDAC-REGRESSION.md) · [Range issue](docs/BLUETOOTH-RANGE.md) · [Historical v1.2 README](docs/releases/v1.0.0-README.md)

## Credits and licence

TempoTec firmware remains TempoTec's; HiBy visual assets remain HiBy's. Kae0, losber and tooling contributors retain attribution in [CREDITS.md](CREDITS.md). The existing MIT licence covers project tooling/documentation, not proprietary firmware, HiBy artwork or LDAC code. See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).

Not affiliated with or endorsed by TempoTec or HiBy.
