# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.1] — 2026-09-15

### Full Mod fixes

- Restored the official v1.3 music listview, removing the album-opening latency introduced by the themed listview.
- Restored the stock long-press Power shutdown countdown/overlay.
- Corrected the Balance Quick Settings artwork using the native Balance glyph and modern tile styling.

### Unchanged

- Stock + LDAC Fix is unchanged from v1.1.0.
- The LDAC decoder correction is unchanged.
- PEQ, Bluetooth components, kernel, radio firmware and updater/recovery are unchanged.

### Upstream / device limitations

- Album-art screensaver track/artwork refresh has the same short delay on official v1.2/v1.3.
- Bluetooth RF/link margin remains limited under high-rate LDAC and difficult RF conditions; the exact cause is unconfirmed.

## [1.1.0] — 2026-09-12 (TempoTec v1.3 generation)

Two hardware-tested editions: Stock + LDAC Fix and Full Mod, both using the original hardware-tested release images. Project tag `v1.1.0`.

### Based on official TempoTec v1.3

- Added Parametric EQ and real-time Bluetooth search.
- Official stability fixes resolved previously observed freeze/reboot behavior, including the severe Bluetooth signal-loss case and reported artwork-related instability. The historical cover's exact JPEG encoding/dimensions/filesize are not established; no precise image condition is claimed.
- Other upstream bug fixes, as stated in TempoTec's changelog.

### Fixed by this project

- Isolated the v1.3 digital LDAC corruption to the receiver decoder through hardware testing.
- Identified an additional downstream coefficient-suppression gate; author/purpose unknown.
- The one-byte decoder patch bypasses only this condition, retains the v1.3 decoder and produces hardware-confirmed clean LDAC playback. This does not fix Bluetooth range or account for the official stability improvement.
- Relocated the Full Mod player patch to file offset `0x38240`, independently validated against v1.3 bytes and surrounding logic.
- Selectively ported Full Mod UI/visual fixes; corrected final launcher backgrounds, play/pause image mapping and popup text.

### Added in Full Mod

- HiBy-style launcher/categories/Now Playing, battery-fill and charging corrections, three-state gain artwork, correctly named working brightness control, missing layout elements, tint exclusions and TempoTec branding.
- About/developer route and colour theme; TF image/database cache and DAC persistence; guarded read-ahead/cache-pressure tuning and UBIFS `sync → noatime` policy (also removes synchronous writes).
- Complete final file list in `build/v1.3/full-mod-manifest.json`. Stock Fix has none of these additions.
- Historical documentation below claims a restored pull-down volume slider. Artifact review establishes brightness-only in the shipped old theme and tested final port; volume objects are retained hidden in the final port. Historical entry preserved verbatim, not used as proof of shipped behavior.

### Known issues

- Bluetooth range/interference remains under investigation. Higher LDAC rates are unreliable; lower rates may also cut in crowded/interference-heavy environments. AAC is the reliable fallback in the observed normal-use scenarios.

## [1.0.0] — 2026-08-15

First public release. Built against TempoTec `V3_ANALOG_2025` v1.2, build `202601301221`.

`v3_analog_2025.upt` — md5 `07dd695255f398a6893f0708c770f0a2`

### Added
- The current HiBy OS design ported to the V3 Blaze, by way of Kae0's V3 Analog build:
  launcher, categories, Now Playing, pull-down menu.
- Brightness slider in the pull-down, working (the binary only wires it under one exact name).
- Volume slider restored alongside it.
- Missing middle gain state drawn for the pull-down icon and the settings switch.
- *Settings → About* enabled, which is the route to developer mode and adb.
- *Settings → Colour theme* (the firmware's own accent picker) enabled.
- Image cache, database cache, filesystem read-ahead and `noatime`: the music database builds
  much faster.

### Fixed
- Battery fill vanishing below ~30% charge, and the doubled battery on the charging screen.
  Both are defects in the donor artwork, present on its original device too.
- Playback quality misreported once the image cache was enabled — four-byte patch to
  `hiby_player` at `0x00436a00`.
- 14 layout files missing elements the binary looks up by name.
- Accent tinting applied to things it should not touch (colour-picker swatches, QR codes) and
  missing from things it should (volume bar).
- Donor artwork carrying another manufacturer's branding; TempoTec's restored.

### Known limitations
- No red low-battery frame (traded away to fix the battery fill).
- No PEQ yet.
