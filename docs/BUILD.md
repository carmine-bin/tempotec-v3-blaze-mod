# Build v1.3 firmware

Run commands from the repository root. Supply the official TempoTec V3 Blaze v1.3 UPT with SHA-256:

```text
5aa1bf262e9241737086076eef0f238e54e75ae226fa0c845d126de11ac01e95
```

TempoTec distributes v1.3 only over the air. Obtain the official UPT as described in [Getting the official v1.3 firmware](INSTALL.md#getting-the-official-v13-firmware). The official firmware is not included in this repository.

`--input` accepts any filename: the builder identifies the official firmware by its SHA-256, not its name. A backup such as `v3_analog_2025.upt.stock` works as-is.

Required: Linux, Python 3 without `-O`, squashfs-tools with LZO and TAR input, xorriso, bsdtar/libarchive, binutils/readelf and clang with a MIPS32 target. The recorded v1.1.2 build used squashfs-tools 4.7.5, xorriso 1.5.8.pl02 and clang 22.1.8. No root is required: numeric-owner TAR records supply filesystem metadata explicitly.

## Commands

Use a new output directory for each build:

```bash
python3 build/build-v1.3.py stock-fix --input ~/v3_analog_2025.upt.stock --output build/reproductions/stock-fix --reference downloads/V3-Blaze-v1.3-Stock-LDAC-Fix.upt
python3 build/build-v1.3.py full-mod --input ~/v3_analog_2025.upt.stock --output build/reproductions/full-mod --reference downloads/V3-Blaze-v1.3-Full-Mod-v1.1.2.upt
```

`--reference` is optional. Every build must match its pinned UPT SHA-256 in [release.json](../build/v1.3/release.json). With a reference, the builder also independently extracts and compares all files, metadata, hardlink groups and kernel bytes. An equivalent reference can have a different local filename.

Outputs include the edition-named UPT and `.sha256`, `FILE-MANIFEST.json`/`.tsv`, `FINAL-VERIFICATION.json`, `REPRODUCTION-REPORT.json` and extraction logs. Full Mod adds `BINARY-PATCHES.json`, `UI-PAYLOAD-MANIFEST.json` and `HOOK-VALIDATION.json`. Failed output directories are retained for diagnosis; rerun in a new directory.

## Source and checks

Stock + LDAC Fix changes only decoder byte `0x3b82`, `40 → 00`. It preserves official content and metadata elsewhere, including 208 hardlink groups. [Stock manifest](../build/v1.3/stock-fix-manifest.json).

Full Mod imports only [manifest-listed](../build/v1.3/full-mod-manifest.json) resources/configuration/scripts from `theme/v1.3/`. Its manifest has 611 changed or added regular files and two new directories relative to official v1.3. The player is generated from the official binary: the existing next-track metadata NOP is applied first, then the exact validated [UI hooks](../build/v1.3/ui/hooks.S). Generated layouts must equal the checked-in resources. Input/final hashes, original bytes, delay slots, LLVM assembly and instruction-harness checks fail closed.

[Full Mod metadata](../build/v1.3/full-mod-metadata.json) preserves the physically tested image's modes, numeric owners, timestamps and symlink targets, including its existing lack of hardlinks. It is never applied to Stock. Metadata is not normalized during release integration.

Both rootfs images are built from source through TAR and mksquashfs. The old `hardware-tested-rootfs.squashfs` and `hardware-tested-iso-header.bin` remain historical audit snapshots; the production builder does not read them or substitute them for generated output.

Validation covers:

- Official input SHA-256, Rock Ridge/Joliet file trees and OTA chunk/hash chains.
- Layout parsing with duplicate keys retained, 1,283 official widget/type/parent contracts, indexed-image references, construction order, PNG CRCs and shell syntax.
- Exact changed-file allowlists and binary byte deltas; protected system/audio components remain official except for the decoder correction.
- SquashFS 4.0/LZO, 131,072-byte blocks, export flags, creation time and edition-specific IDs/inodes/hardlinks. Rootfs stays within the original 40,108,032-byte write span, with zero padding checked.
- Complete content/metadata/link comparison before packaging and after reconstruction from the final UPT.
- Unchanged kernel chunks, uImage header/payload CRC32 and decompressed kernel bytes.
- OTA declarations, chunk indices and previous-MD5 filename chains; ISO names, ownership, modes and timestamps.

Five official `hl_json` files contain trailing commas: `hl_break_point_d.json`, `hl_digital_filter_d.json`, `hl_dsd_output_d.json`, `hl_play_mode_d.json` and `hl_replaygain_type_d.json`. They are accepted only when byte-identical to official v1.3 and are reported as exceptions. Modified configuration must parse.

The v1.1.2 Full Mod UPT reproduces the physically validated UI Fixes Test byte for byte. Stock reproduces its unchanged published UPT. Hashes and verification results are in the [candidate manifest](releases/v1.1.2-manifest.json) and [evidence](evidence/release-v1.1.2-verification.json).

Historical `theme/theme_port/`, asset helpers and `build/build-upt-v3.sh` target v1.2. The old builder requires `BUILD_HISTORICAL_V12=1`; it is not the current interface. Donor helpers may require `BLAZE_STOCK_ROOTFS` and `V3_ANALOG_ROOTFS`. See the unchanged [v1.0.0 build record](releases/v1.0.0-BUILD.md).
