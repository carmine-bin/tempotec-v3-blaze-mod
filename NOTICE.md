# Firmware and artwork notice

## Licence scope

The MIT [licence](LICENSE) covers only the original work in this repository: the build scripts, the binary-analysis and validation utilities, and the documentation.

It does not cover:

- The firmware images distributed in Releases, or the official TempoTec firmware they are built from.
- The graphical assets contained in those images or in `theme/`, including imported HiBy artwork and TempoTec stock assets.
- Proprietary player, litegui and LDAC code. These are not claimed as original work.

Modified TempoTec firmware and imported HiBy artwork retain their respective rights holders. [Credits](CREDITS.md) identify the port and research contributors.

## Firmware contents

Both editions retain the official v1.3 kernel. Stock + LDAC Fix changes one decoder byte. Full Mod adds the resources, configuration, scripts and player changes in its [manifest](build/v1.3/full-mod-manifest.json). The [technical notes](docs/HOW-IT-WORKS.md) and [UI investigation](docs/UI-FIXES.md) describe their scope.

Firmware is supplied for personal use and research. Flashing is at your own risk and may affect warranty coverage. Not affiliated with, endorsed by or supported by TempoTec or HiBy.

Rights holders can contact the maintainer or open an issue to request removal of repository contents.
