# Reproduce the two official-v1.3 editions

Release images are the original hardware-tested Stock + LDAC Fix and Full Mod images. A new build is a **reproduction**, not an automatic replacement for either tested image. Firmware/base version v1.3 is separate from project tag v1.1.0.

## Inputs and tools

Linux, Python 3 (without `-O`), squashfs-tools with LZO/TAR input support, xorriso, bsdtar (libarchive), binutils/readelf. No root needed: a metadata-explicit numeric-owner TAR preserves stock owners, modes, special bits, timestamps, symlinks and hardlink groups. Never use a blanket all-root repack. Historical fakeroot instructions are preserved in [v1.0.0-BUILD.md](releases/v1.0.0-BUILD.md).

Supply the official TempoTec V3 Blaze v1.3 UPT from TempoTec's firmware distribution. It must have SHA-256:

```
5aa1bf262e9241737086076eef0f238e54e75ae226fa0c845d126de11ac01e95
```

The builder extracts ISO payloads and reconstructs kernel/rootfs automatically. No proprietary player/decoder binary or official firmware input is committed. Current resources live in `theme/v1.3/`; the previous `theme/theme_port/` and scripts are historical sources, not a v1.3 overlay.

## Build separately

From the repository root, use a new, nonexistent output directory for each invocation:

```bash
python3 build/build-v1.3.py stock-fix --input inputs/official-v1.3.upt --output build/reproductions/stock-fix --reference downloads/V3-Blaze-v1.3-Stock-LDAC-Fix.upt
python3 build/build-v1.3.py full-mod --input inputs/official-v1.3.upt --output build/reproductions/full-mod --reference downloads/V3-Blaze-v1.3-Full-Mod.upt
```

`--reference` is optional for building, but required to prove equivalence to the hardware-tested edition. It checks the reference's exact expected UPT hash, independently extracts it and compares every path's content, ownership, permissions/special bits, timestamps, symlink target, hardlink topology and the kernel. Directory sizes may change during compression and are not security metadata. Use the release filenames and hashes in the [release manifest](releases/release-manifest.json) to identify reference images.

Output: `reproduced.upt`, its `.sha256`, `FILE-MANIFEST.json`/`.tsv`, `FINAL-VERIFICATION.json` and `REPRODUCTION-REPORT.json`, plus retained extraction/audit logs. Existing outputs are never overwritten or deleted. Failed build directories remain for diagnosis; rerun in another empty location after correcting the failure.

## Verified v1.1.0 reproduction results

On the recorded toolchain, both editions reproduced the hardware-tested UPT byte-for-byte, including identical SHA-256. The filesystem comparison also matched content, ownership, modes/special bits, timestamps, symlinks and hardlink topology. Results are retained in the [Stock Fix reproduction report](evidence/reproducibility-v1.1.0.json) and [Full Mod reproduction report](evidence/reproducibility-v1.1.0.json). This does not automatically hardware-validate a changed build.

Five unrelated official configuration files under `/usr/resource/hl_json/` contain trailing commas: `hl_break_point_d.json`, `hl_digital_filter_d.json`, `hl_dsd_output_d.json`, `hl_play_mode_d.json` and `hl_replaygain_type_d.json`. The validator permits them only when byte-identical to the official base and reports these exceptions. All layouts and modified configuration files must parse successfully.

Historical asset-generation helpers in `build/scripts/` target `theme/theme_port/`, not the current v1.3 release resources. Helpers needing comparison images require `BLAZE_STOCK_ROOTFS` and, for donor branding, `V3_ANALOG_ROOTFS`, pointing to extracted firmware rootfs trees. They are not required to reproduce v1.1.0 and should not be run against immutable release resource snapshots.

## Intentional filesystem changes

**Stock Fix:** only `/usr/lib/libldacdec.so.1`, exactly byte `0x3b82`, `40 → 00`. Original v1.3 decoder hash and instruction bytes must match before patching; final hash must match the released Stock + LDAC Fix decoder. No theme, player, config or script changes. [Stock manifest](../build/v1.3/stock-fix-manifest.json).

**Full Mod:** exact [609-entry manifest](../build/v1.3/full-mod-manifest.json): 560 modified regular files, 47 new PNGs and two new directories. Categories: 114 layouts, 487 assets/tint-list files, two JSON configs, two scripts, player and decoder. The configs enable only about/color, DAC persistence and TF image/database cache. Scripts add guarded read-ahead/cache-pressure tuning and UBIFS `sync → noatime`. Player patch only at `0x38240`, original `08 da 10 0c`, final NOP, delay slot untouched; exact original/final SHA-256 checked. Both PEQ layouts remain official v1.3.

The build imports only manifest-listed final resource/config/script bytes. Player and decoder are patched from verified official binaries, never supplied as old replacements. Both binary ELF metadata outputs must stay identical to official v1.3. Original bytes/hashes, changed-byte locations and final hashes fail closed.

## Validation and packaging

- Verify official UPT hash, both ISO naming trees, actual extracted payload hashes and OTA declarations/chunk chains before accepting the input.
- Preserve all official paths, metadata and hardlinks; generate an exact changed-files manifest. Stock Fix must have one changed file. Full Mod must match its complete documented allowlist.
- Parse all layouts using duplicate-key-safe JSON, preserve official widget/type/parent and indexed-image contracts, and enforce properties before construction markers. Check no new missing image references, PNG chunk CRCs, modified configuration JSON and shell syntax. Any invalid unrelated stock JSON must remain byte-identical and is reported as a stock exception, never silently repaired.
- Rebuild SquashFS 4.0/LZO, 131072-byte blocks, stock flags/export table/IDs/no-xattrs and original creation time; retain the 40,108,032-byte write span with verified zero padding.
- Re-extract and compare all files/metadata/links before packaging and again from final UPT. Keep the exact official v1.3 kernel; verify uImage header/payload CRC32 and decompressed equality.
- Use official ISO as template, replacing only rootfs chunks/list and rootfs checksum in `ota_update.in`. Recalculate all hashes; check contiguous chunk indices, previous-chunk filename chains, lengths/whole-image MD5, Rock Ridge/Joliet trees, ISO metadata and identifiers. Kernel chunks and updater control files stay intact.

UPT/compressed layout hashes may differ despite identical filesystem content; report both comparisons explicitly. **Do not silently substitute a reproduction for a hardware-tested release image.** Rename the chosen image to `v3_analog_2025.upt` only when preparing to flash; see [INSTALL.md](INSTALL.md) and [RECOVERY.md](RECOVERY.md).

The old `build/build-upt-v3.sh` is protected as historical v1.2 tooling; it requires explicit `BUILD_HISTORICAL_V12=1` and is not the current build interface.
