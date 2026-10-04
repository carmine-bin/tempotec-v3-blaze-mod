# Installation

For TempoTec V3 Blaze (`V3_ANALOG_2025`) only. The older V3 Analog uses different hardware. Both editions use the same microSD updater.

Read [Recovery](RECOVERY.md) before flashing.

**A file named `update.upt` in the microSD root takes priority over `v3_analog_2025.upt`, including updates started from Settings. Remove or rename any `update.upt` before installing.**

## Getting the official v1.3 firmware

Keep a copy of the official v1.3 firmware before installing either edition. It is the only way back to 100% official firmware, and it is the required input for [building](BUILD.md) the editions yourself. TempoTec's website does not offer the v1.3 UPT yet; v1.3 is only distributed over the air (OTA). The OTA update leaves the official UPT in the microSD root as `v3_analog_2025.upt`, the same name and location these instructions use for the mod.

1. **If you already updated to v1.3 over the air:** the official UPT is probably still in the root of your microSD as `v3_analog_2025.upt`. Rename it to `v3_analog_2025.upt.stock` and also copy it to your computer.
2. **Starting from scratch:** download the official v1.2 firmware from [TempoTec's firmware download page](https://www.tempotec.net/pages/firmware-download). Choose the entry **"TempoTec V3 Blaze Firmware V1.2"**. Do **not** use "TempoTec V3 Firmware V1.0": it is for the older V3, not the Blaze. The download is a `.zip`: extract it and use the `.upt` file inside. The zip also contains a factory image for Ingenic USB boot; keep it, because it is what the last-resort procedure in [Recovery](RECOVERY.md) needs. Rename the UPT to `v3_analog_2025.upt`, copy it to the microSD root and install it from Settings → Firmware update → Update via micro SD card. Then update to v1.3 over the air and do the same as in step 1. Going from v1.3 to v1.2 via microSD and back to v1.3 over the air was tested on a physical V3 Blaze. At the time of writing, the page only offers v1.2; v1.3 is distributed over the air only.
3. **In both cases**, check that its SHA-256 matches the official v1.3 hash listed in [Build](BUILD.md):

   ```text
   5aa1bf262e9241737086076eef0f238e54e75ae226fa0c845d126de11ac01e95
   ```

   If it differs, the file is not the official v1.3 UPT; do not rely on it as a backup.

```bash
sha256sum v3_analog_2025.upt.stock
```

Windows: `certutil -hashfile v3_analog_2025.upt.stock SHA256`.

## Install

1. **If there is a `v3_analog_2025.upt` in the microSD root (for example, the one left by the OTA update), rename it to `v3_analog_2025.upt.stock` before copying the mod. Otherwise the mod will overwrite it and you will lose your copy of the official firmware.**
2. Choose an edition from [Releases](https://github.com/carmine-bin/tempotec-v3-blaze-mod/releases). Check its SHA-256 against the matching release manifest or `SHA256SUMS`.
3. Rename the selected UPT to exactly `v3_analog_2025.upt`. Copy it to the microSD root, eject safely and insert the card. Check for a doubled extension if your file manager hides extensions.
4. Open Settings → Firmware update → Update via micro SD card and confirm. The device sets its boot flag, restarts into recovery, flashes and reboots.
5. Wait for flashing and initial boot to finish. Keep power connected if used; do not interrupt the updater.

Linux verification:

```bash
sha256sum V3-Blaze-v1.3-Stock-LDAC-Fix.upt
sha256sum V3-Blaze-v1.3-Full-Mod-v1.1.2.upt
```

Windows: `certutil -hashfile <downloaded-file> SHA256`. Stop if the checksum differs. Renaming a file leaves its checksum unchanged.

Both editions should boot with official v1.3 PEQ and Bluetooth search, with the LDAC audio corruption corrected. Full Mod adds the custom interface, an About entry in Settings, theme colors and brightness control. Its pull-down volume objects remain hidden.

Developer mode and ADB are off by default in both editions and work as in the official firmware: tap About 10 times to enable them. In the official interface and in Stock + LDAC Fix, About is in the home menu. Full Mod's HiBy-style launcher has no About entry, so Full Mod shows About in Settings instead (the official settings configuration hides that entry because the home menu already has it). This project does not enable ADB or change how developer mode works.

## Backup and restore

Keep backups on the card as `v3_analog_2025.upt.stock` or `v3_analog_2025.upt.bak`; the updater ignores those names.

- **Closest to official v1.3:** flash the Stock + LDAC Fix edition. It is the official v1.3 firmware with a single byte changed in the LDAC decoder; see [LDAC receiver artifacts](LDAC-RECEIVER-ARTIFACTS.md).
- **100% official firmware:** rename your `v3_analog_2025.upt.stock` to `v3_analog_2025.upt` and update from the microSD card as in the install steps.

If the system cannot boot, use [Recovery](RECOVERY.md).
