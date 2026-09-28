# Installation

For TempoTec V3 Blaze (`V3_ANALOG_2025`) only. The older V3 Analog uses different hardware. Both editions use the same microSD updater.

Read [Recovery](RECOVERY.md) before flashing. Keep official firmware on the card as `v3_analog_2025.upt.stock`; rename it only when restoring stock. A spare named `update.upt` takes priority over `v3_analog_2025.upt`, including updates started from Settings.

1. Choose an edition from [Releases](https://github.com/carmine-bin/tempotec-v3-blaze-mod/releases). Check its SHA-256 against the matching release manifest or `SHA256SUMS`.
2. Rename the selected UPT to exactly `v3_analog_2025.upt`. Copy it to the microSD root, eject safely and insert the card. Check for a doubled extension if your file manager hides extensions.
3. Open Settings → Firmware update → Update via micro SD card and confirm. The device sets its boot flag, restarts into recovery, flashes and reboots.
4. Wait for flashing and initial boot to finish. Keep power connected if used; do not interrupt the updater.

Linux verification:

```bash
sha256sum V3-Blaze-v1.3-Stock-LDAC-Fix.upt
sha256sum V3-Blaze-v1.3-Full-Mod-v1.1.2.upt
```

Windows: `certutil -hashfile <downloaded-file> SHA256`. Stop if the checksum differs. Renaming a file leaves its checksum unchanged.

Both editions should boot with official v1.3 PEQ and Bluetooth search, with the LDAC audio corruption corrected. Full Mod adds the custom interface, About/developer access, theme colors and brightness control. Its pull-down volume objects remain hidden. Persistent database/settings state can affect the first boot.

To restore stock, rename your official backup to `v3_analog_2025.upt` and repeat the update. If the system cannot boot, use [Recovery](RECOVERY.md).
