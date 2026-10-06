# Changelog

User-facing changes in each release. "Full Mod" and "Stock + Fixes" (named "Stock + LDAC Fix" before 1.2.0) are the two editions published since 1.1.0. Notes on where historical claims came from are kept in [changelog provenance](docs/evidence/CHANGELOG-PROVENANCE.md).

## [1.2.1] — 2026-10-06

Based on official TempoTec firmware v1.3. Full Mod was tested on physical V3 Blaze hardware.

### Fixed

- Full Mod: below 16 % the battery icon turned solid red and hid the remaining level. The level now keeps the theme color and the battery frame turns red instead, as on the official firmware. See [UI fixes](docs/UI-FIXES.md#low-battery-indicator-v121).
- Full Mod: the low-battery notice showed an empty grey card. It now shows its message.
- Full Mod: the battery frame's corners and cap are drawn solid.

### Changed

- Stock + Fixes is unchanged from 1.2.0.

### Known issues

- Full Mod: the pull-down menu's battery icon keeps its white frame at low charge.
- With the album-art screensaver active, track information and artwork can take about 1.5 seconds to update after a track change. Official TempoTec v1.2 and v1.3 behave the same.

## [1.2.0] — 2026-10-05

Based on official TempoTec firmware v1.3. Both editions were tested on physical V3 Blaze hardware.

### Fixed

- Both editions: Bluetooth Receiver dropouts. BlueZ kept the radio busy with LE background scanning and fast-connectable page scanning while receiving audio, so the source could not sustain LDAC 990 kb/s even at close range and discarded audio. `/etc/bluetooth/main.conf` now sets `ControllerMode = bredr` and `FastConnectable = false`. In testing, LDAC 990 kb/s went from about 60 % dropped audio next to the phone to none, and now holds up to about 12 m through two doors. See [Bluetooth Receiver dropouts](docs/BLUETOOTH-RANGE.md).

### Changed

- Stock + LDAC Fix is renamed Stock + Fixes (`V3-Blaze-v1.3-Stock-Fixes-v1.2.0.upt`). It changes two files from official v1.3: the LDAC decoder byte and `main.conf`.
- The Blaze no longer uses Bluetooth LE. No feature that needs it was found.
- Incoming Bluetooth connections can take up to about a second longer to start (standard page scan).
- Full Mod interface, audio and playback are unchanged from 1.1.2.

### Known issues

- With the album-art screensaver active, track information and artwork can take about 1.5 seconds to update after a track change. Official TempoTec v1.2 and v1.3 behave the same.
- Beyond about 12 m with walls in between, LDAC 990 kb/s still drops out and the source lowers its rate. This is the physical limit of the link.

## [1.1.2] — 2026-09-28

Based on official TempoTec firmware v1.3. Validated on physical V3 Blaze hardware.

### Fixed

- Full Mod: the shutdown screen did not cover the whole display when opened from Now Playing.
- Full Mod: headers and top spacing were wrong on pages opened from the Now Playing menu.
- Full Mod: changing the theme color returned to Music → Songs instead of the main screen.
- Full Mod: Settings cards were corrupted when the scrollbar disappeared after scrolling.

### Changed

- Stock + LDAC Fix is unchanged from 1.1.1. Full Mod audio and playback behavior is unchanged.

### Known issues

- With the album-art screensaver active, track information and artwork can take about 1.5 seconds to update after a track change. Official TempoTec v1.2 and v1.3 behave the same.
- Bluetooth reception has limited link margin, particularly with sustained high-bitrate LDAC and in difficult RF conditions. AAC is more reliable. The cause is unknown. See [Bluetooth range](docs/BLUETOOTH-RANGE.md).

## [1.1.1] — 2026-09-15

Based on official TempoTec firmware v1.3.

### Fixed

- Full Mod: opening an album was slow. The official v1.3 music list is restored in place of the themed one.
- Full Mod: the long-press Power shutdown countdown was missing. The stock countdown and overlay are restored.
- Full Mod: the Balance tile in Quick Settings used incorrect artwork. It now uses the native Balance icon with the modern tile style.

### Changed

- Stock + LDAC Fix is unchanged from 1.1.0. The LDAC decoder correction, PEQ, Bluetooth components, kernel, radio firmware and updater/recovery are unchanged.

### Known issues

- With the album-art screensaver active, track information and artwork take a moment to update after a track change. Official TempoTec v1.2 and v1.3 behave the same.
- Bluetooth link margin is limited with high-bitrate LDAC and in difficult RF conditions. The cause is unknown.

## [1.1.0] — 2026-09-12

First release based on official TempoTec firmware v1.3, and the first with two editions: Stock + LDAC Fix and Full Mod. Both were tested on physical V3 Blaze hardware.

### Added

- From official v1.3: Parametric EQ and real-time Bluetooth search.
- Stock + LDAC Fix edition: official v1.3 with only the LDAC decoder correction.
- Full Mod: HiBy-style launcher, categories and Now Playing; corrected battery fill and charging artwork; three-state gain icons; working brightness control; missing layout elements; accent-tint exclusions; TempoTec branding.
- Full Mod: Settings → About (route to developer mode) and color theme; TF-card image and database cache; DAC-setting persistence; guarded read-ahead and cache-pressure tuning; UBIFS mounted with `noatime` instead of `sync`. The complete file list is in the [Full Mod manifest](build/v1.3/full-mod-manifest.json).

### Fixed

- Bluetooth Receiver LDAC audio corruption introduced by official firmware v1.3. A one-byte decoder patch bypasses an extra coefficient-suppression rule in the v1.3 decoder; clean LDAC playback was confirmed on hardware. This does not change Bluetooth range. See [LDAC receiver artifacts](docs/LDAC-RECEIVER-ARTIFACTS.md).
- From official v1.3: freezes and reboots seen on v1.2, including the severe Bluetooth signal-loss case and reported artwork-related instability, plus the other fixes in TempoTec's changelog.
- Full Mod: launcher backgrounds, play/pause image mapping and popup text.

### Changed

- Rebased from official TempoTec v1.2 to v1.3.
- Full Mod: the fix for Now Playing showing the next track's audio quality was ported to the v1.3 player.
- Full Mod: the pull-down shows a brightness slider only; its volume controls are hidden. Volume controls remain available elsewhere.

### Known issues

- Bluetooth range and interference are under investigation. Higher LDAC rates are unreliable; lower rates may also cut out in crowded or interference-heavy environments. AAC is the reliable fallback in normal use.

## [1.0.0] — 2026-08-15

First public release. Based on official TempoTec firmware v1.2 (`V3_ANALOG_2025`, build `202601301221`). Superseded by the 1.1.x releases, which are based on v1.3.

Release file: `v3_analog_2025.upt`, md5 `07dd695255f398a6893f0708c770f0a2`.

### Added

- The current HiBy OS design ported to the V3 Blaze, by way of Kae0's V3 Analog build: launcher, categories, Now Playing and pull-down menu.
- Working brightness slider in the pull-down (the binary only wires it under one exact name).
- Missing middle gain state drawn for the pull-down icon and the settings switch.
- Settings → About enabled, which is the route to developer mode and adb.
- Settings → Colour theme (the firmware's own accent picker) enabled.
- Image cache, database cache, filesystem read-ahead and `noatime`: the music database builds much faster.

### Fixed

- Battery fill vanishing below ~30% charge, and the doubled battery on the charging screen. Both are defects in the donor artwork, present on its original device too.
- Playback quality misreported once the image cache was enabled (four-byte patch to `hiby_player` at `0x00436a00`).
- 14 layout files missing elements the binary looks up by name.
- Accent tinting applied to things it should not touch (colour-picker swatches, QR codes) and missing from things it should (volume bar).
- Donor artwork carrying another manufacturer's branding; TempoTec's restored.

### Known issues

- No red low-battery frame (traded away to fix the battery fill).
- No PEQ. PEQ arrived with official v1.3 in 1.1.0.
- The 1.0.0 release notes listed a restored pull-down volume slider. It is not visible in current releases: the pull-down has only the brightness slider, and volume controls remain available elsewhere.
