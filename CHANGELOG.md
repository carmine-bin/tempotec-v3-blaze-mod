# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
- Heart and play-mode toggles in the pull-down are hidden; the binary never listens for them.
- No PEQ yet.
