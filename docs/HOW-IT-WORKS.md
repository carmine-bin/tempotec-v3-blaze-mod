# Technical notes

The player loads named widgets from `.view` and `.dlg` resources, with loose PNG artwork under `/usr/resource`. These files live in the read-only rootfs, so persistent changes require rebuilding the firmware.

## Layout contracts

Widget names are part of the player API. The brightness callback expects `pull_down_menu_pb`; the donor name `pull_down_menu_bklight_pb` produced a draggable control without a working callback. Lookups also depend on widget type and parent. Some search only direct children.

The USB DAC builder looks up six fixed names and dereferences them without a null check; a load in a MIPS call's delay slot exposed the missing-widget crash. Preserve names, types, parents and indexed `img_path_N` states. Blaze gain has three states, so two-state donor artwork omitted the middle level.

Repeated JSON keys represent sibling widgets. Property order relative to construction markers also matters. The [ordered-pair parser](../build/v1.3/layout.py) preserves both. Standard JSON dictionaries cannot safely round-trip these layouts. Missing PNGs can be cosmetic—38 dangling references were recorded in the historical stock audit—but malformed layout syntax can prevent boot. Current checks reject newly missing image references.

## Artwork and tinting

Battery fill is cropped, not scaled: the engine takes the first `h × pct` rows and draws them at `y + h − h × pct`. A donor image containing the outline and terminal produced a second battery inside the frame and lost useful fill at low charge. Full Mod separates a bare fill, sized and positioned to the frame opening, from the static frame. The same correction applies to charging artwork. Offline composites at 100%, 59%, 25% and 10% reproduced and checked the crop behavior.

Accent tinting happens when PNGs load. `litegui/theme1/no_skin_list.txt` controls opt-outs; protect color swatches and QR artwork while allowing intended controls to follow the accent. Preserve Windows-style paths and CRLF endings. A late bind-mount cannot reliably test already-loaded colors.

## Configuration and I/O

Full Mod enables About/color settings, DAC-setting persistence and TF image/database cache flags. The startup script applies MMC read-ahead `2048` and cache pressure `50` only where the relevant paths exist. UBIFS mounting changes `sync` to `noatime`, removing synchronous writes as well as access-time updates. These settings are retained from the tested Full Mod; no quantified speed or stability benefit is claimed for each flag.

The pull-down retains brightness and hides its existing volume/decorative lookup objects. Other volume controls remain available. Official PEQ/filter layouts are preserved.

## Next-track metadata patch

A next-track query copies its output structure, then parses the next file into a shared current-track buffer. The identified operation-`0x1f` callers use the returned path, while API operation 4 reads that shared buffer. Parsing can overwrite current title, artist, album and format fields; the parser also clears pointers without freeing their previous strings.

In v1.3, file offset `0x38240` / VA `0x438240` changes `08 da 10 0c` (`jal 0x436820`) to a NOP. Output copy (`0xa88` bytes), selection restoration, unlock/return and the `addiu a0,a0,4` delay slot remain. The shared buffer is at `0x988f90`. The historical v1.2 patch was at `0x36a00` / VA `0x436a00`; that offset is not reused in v1.3.

Six instruction-harness cases covered valid/null output, absent next track, absent lock callback and API 4 with/without output. External calls were mocked. These checks establish the isolated path, not every indirect caller or the complete audio pipeline. [Original player validation](evidence/full-mod-player-validation.json) records that work. Current Full Mod adds the separately documented [UI hooks](UI-FIXES.md).

## Migration to official v1.3

| Comparison input | SHA-256 |
|---|---|
| Official v1.2 | `561797a3e1041e6cd38a909bef1cf2950eac97d589935bc86eec72ebab39d811` |
| Previous v1.2 Full Mod | `bb26dbf8fbd9ebb49972adee978154eb20d6f16bc4772a6d811ea3e452926e97` |
| Official v1.3 | `5aa1bf262e9241737086076eef0f238e54e75ae226fa0c845d126de11ac01e95` |

Official v1.3 supplies the complete current base, including PEQ, real-time Bluetooth search and stability fixes. The comparison found 208 non-timestamp path differences from v1.2 across the player/server, Bluetooth, kernel/modules, USB and resources. Full Mod ports an explicit resource/configuration allowlist rather than replacing whole directories or importing old system components. All 151 official layouts and their required named contracts remain.

The v1.3 base improved previously observed freezes/reboots. In a severe Bluetooth degradation test, connection loss no longer rebooted the player; it recovered when the link returned. Artwork-related instability was also reported resolved. The historical trigger's JPEG encoding, dimensions and file size were not retained, so progressive JPEG cannot be identified as its cause. These observations concern the official base, not the decoder patch.

Both editions use the same one-byte [LDAC correction](LDAC-RECEIVER-ARTIFACTS.md). It has no demonstrated dependency on PEQ, the theme or the next-track patch. The [Bluetooth link-margin issue](BLUETOOTH-RANGE.md) remains unresolved.

The current [builder](BUILD.md) records metadata explicitly in TAR, re-extracts both rootfs stages and checks the final UPT against pinned bytes. It preserves Stock hardlinks and existing Full Mod metadata separately. Historical v1.2 builds used fakeroot; their checks and counts remain in [archived documentation](releases/v1.0.0-BUILD.md).

Reverse-engineering helpers in [build/scripts](../build/scripts) include `xref.py`, `mipsdis.py`, `annotate.py` and `lookup-audit.py`; Ghidra headless was also used. Cross-references must account for `lui`/`addiu` address pairs and MIPS delay slots.
