# Recovery

With the player off, hold **Power + Previous track**. Keep holding past the TempoTec logo until **updater** appears. Releasing at the logo starts the normal system.

A valid `v3_analog_2025.upt` in the microSD root is flashed automatically. Without a usable card/file, recovery waits about 10 seconds and exits without writing. This key combination was tested on the V3 Blaze.

> **Warning:** recovery flashes any valid `v3_analog_2025.upt` it finds in the microSD root without asking, including the official UPT left there by an OTA update. Check which file is in the root before entering recovery. See [Installation](INSTALL.md#getting-the-official-v13-firmware).

Keep backups as `.upt.stock` or `.upt.bak` ([Backup and restore](INSTALL.md#backup-and-restore)). The updater tries the configured filename, then `update.upt`, then `v3_analog_2025.upt`; a leftover `update.upt` therefore overrides the standard device filename, even for an update initiated from Settings.

If the system cannot boot:

1. Hold Power for 10–15 seconds to force the player off.
2. Insert a card containing known-good firmware named `v3_analog_2025.upt` at its root. Remove any `update.upt`.
3. Hold Power + Previous track past the logo until updater appears.
4. Let recovery flash and reboot without interruption.

These packages write the main kernel/rootfs and retain the official kernel. They leave the bootloader and recovery partitions untouched. Recovery can therefore reinstall the main system after a bad UI build, provided recovery and the storage remain usable.

If recovery cannot start, the last resort is Ingenic USB boot with Power + Next track and [Ingenic-community/Cloner](https://github.com/Ingenic-community/Cloner). It needs the factory `.ingenic` image included in the official v1.2 zip from TempoTec's firmware download page; see [Getting the official v1.3 firmware](INSTALL.md#getting-the-official-v13-firmware). That recovery procedure has not been exercised on this device; seek help before attempting a whole-flash rewrite.

## Flash layout

| Partition | Contents |
|---|---|
| `mtd0` | u-boot, 512 KiB |
| `mtd1` / `mtd2` | main kernel, 5 MiB / rootfs, 45 MiB |
| `mtd3` / `mtd4` | recovery kernel, 5 MiB / rootfs, 24 MiB |
| `mtd5` | boot selector and boot-logo flag, 512 KiB |
| `mtd6` | user data, 45 MiB, UBIFS |

u-boot reads `mtd5` to select `ota:kernel` or `ota:kernel2`. The updater writes partitions by name and restores the selector after updating.
