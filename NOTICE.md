# Notice on firmware and artwork

The two v1.3 release images are modified TempoTec firmware for the V3 Blaze. The firmware remains TempoTec's; HiBy OS, proprietary player/litegui code and visual assets retain their respective rights holders. LDAC code is not claimed as project-owned. The MIT licence applies to original project tooling/documentation, not proprietary firmware or imported artwork. [CREDITS.md](CREDITS.md) preserves TempoTec, HiBy, Kae0, previous contributors and tooling attribution.

Both editions keep the official v1.3 kernel byte-for-byte. Stock + LDAC Fix changes only one byte in `/usr/lib/libldacdec.so.1`. Full Mod adds the selective UI/resource/config/script changes and four-byte relocated player patch listed in its [complete manifest](build/v1.3/full-mod-manifest.json). No old v1.2 Bluetooth/audio/kernel components are overlaid. Internal code authorship is not inferred from who distributed the firmware; the downstream LDAC gate's author/purpose remain unknown.

The [technical documentation](docs/HOW-IT-WORKS.md), [LDAC investigation](docs/LDAC-REGRESSION.md) and [build instructions](docs/BUILD.md) describe the changes. Hardware-tested release artifacts and newly reproduced images are distinguished. Bluetooth range/interference remains unresolved.

## Purpose and risk

Distributed for personal use, research and the device-modding community. Flashing modified firmware is at your own risk and may void your warranty.

Not affiliated with, endorsed by, or supported by TempoTec or HiBy.

## Rights holders

If you are TempoTec, HiBy or another rights holder and object to repository contents, open an issue or contact the maintainer directly for removal.
