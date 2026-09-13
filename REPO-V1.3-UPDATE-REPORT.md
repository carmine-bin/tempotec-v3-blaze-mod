# Repository v1.3 update report

**Local validation snapshot, 2026-09-12. Both editions reproduced byte-for-byte from official v1.3 and match the exact hardware-tested release sources. No commit, push, tag or publication had occurred when this report was prepared.**

Repository: `/home/carmine/v3-porting-analysis/repository`, origin `carmine-bin/tempotec-v3-blaze-mod`, baseline `042380b09b46dd8a34a3a1f46738a9cd3002ab66`. Project tag **v1.1.0** (official firmware base **v1.3**).

## Release images: exact tested bytes

| Edition | Tested original source | Private public-name copy | SHA-256 | MD5 |
|---|---|---|---|---|
| Stock + LDAC Fix | `/home/carmine/v3-ldac-analysis/test2/V3_1.3_TEST2_LDAC_GATE_BYPASS.upt` | `release-staging/V3-Blaze-v1.3-Stock-LDAC-Fix.upt` | `273f56607d477d44bd071c1a3e2097361610c2e403cfddc7ccf51b98a56210d1` | `cd380b93df9a600a5d24cb64585aac88` |
| Full Mod | `/home/carmine/v3-port-ui-state-fix/v3_analog_2025.upt` | `release-staging/V3-Blaze-v1.3-Full-Mod.upt` | `fbb6f356cea7cae73b7af39ade9d32e0e4b0f9fc1eaab4a6ac401f6e92a4c933` | `c09b37baa6fd6a5660e4bbc355bae33c` |

Each is 44,367,872 bytes. Private copies are exact original bytes, not rebuilt substitutes. SHA256SUMS, MD5SUMS and release-manifest.json exist in private staging and documented under `docs/releases/`. Neither firmware is tracked in Git. Final Full Mod hardware identity was clarified by the user's confirmation that the last complete mod was perfect; pending fields in original evidence are explicitly historical. Intermediate black-screen/incomplete-UI builds are excluded.

Stock rootfs SHA-256: `aa3f317b7de8fa07c00f3ecf63bd51f1e3131a521a63daf1ff0a452c0fff2fac`.
Full rootfs SHA-256: `66c3216e74cedb23a6cf5c4d6f7667c0a2d7bc1e04691fe1808a6fc16f56df13`.

## Documentation and resources

- README EN/ES now describe official v1.3, two-edition download/table/checksums, PEQ/search/stability gains, independent decoder correction, Full Mod UI/settings, install filename and unresolved range issue. Technical coverage and all hash/table entries compared.
- CHANGELOG adds clearly separated official/project/Full Mod/known-issue sections. Existing 1.0.0/v1.2 entry is byte-for-byte unchanged.
- Added LDAC-REGRESSION and BLUETOOTH-RANGE, preserving exact gate semantics, TEST 1/2 hardware isolation, origin uncertainty, PEQ independence and separate link-margin symptom. No prohibited PCM ratio included.
- HOW-IT-WORKS retains original reverse-engineering explanations; historical player/gates labeled, PEQ updated, selective v1.3 migration and relocated player validation added. INSTALL adapted for both editions; RECOVERY only receives an edition/rename clarification. Verified recovery body unchanged.
- CREDITS retains TempoTec, HiBy, Kae0, losber/community tooling and adds research acknowledgement. Prior unverified asset-count claims labeled historical; artifact review counted 675 PNGs in the old theme and 680 in the final theme. NOTICE preserves proprietary ownership, project MIT scope and non-affiliation.
- Historical README EN/ES and BUILD archived with relative links adjusted; previous theme and tooling preserved. CONTRIBUTING distinguishes current manifest/layout count from historical instructions.
- Current selective resources: 605 manifest-hashed final layouts/assets/config/scripts under theme/v1.3. No proprietary player/decoder binary copied into the repo. Full/stock file manifests and original/fresh audits retained.

## Build and reproduction results

Interface: `python3 build/build-v1.3.py stock-fix|full-mod --input official.upt --output new-directory --reference tested.upt`. Parameterizes the already verified SquashFS/ISO tooling rather than redoing reverse engineering. The old v1.2 builder is guarded behind BUILD_HISTORICAL_V12=1. Builds refuse existing output directories; fail closed on official checksum, binary hash/instruction mismatches, resources and final validation. Python optimization is explicitly rejected before writes.

| Validation | Stock Fix | Full Mod |
|---|---|---|
| Rebuilt UPT SHA-256 equals tested original | PASS, byte-for-byte | PASS, byte-for-byte |
| Filesystem paths / regular files | 4,172 / 3,485 | 4,221 / 3,532 |
| Decoder change | Only byte 0x3b82: 40→00 | Same exact TEST 2 byte/hash |
| Custom player | Stock unchanged | Exactly four-byte NOP at 0x38240; delay slot/other bytes untouched |
| Layouts / official named contracts | 151 / 1,283 | 151 / 1,283 |
| PNG chunk CRC validation | 883 PNGs in rootfs | 930 PNGs in rootfs |
| New missing image references | None | None |
| Official PEQ/filter layouts | Unchanged | Unchanged |
| File content, owners/modes/special bits/timestamps/links | PASS | PASS |
| Hardlink topology; original symlinks; BusyBox setuid | PASS | PASS |
| Kernel bytes/uImage CRCs/decompressed kernel | Official v1.3, PASS | Official v1.3, PASS |
| SquashFS re-extraction, IDs/flags/compression/padding | PASS | PASS |
| UPT OTA chunk chain/lists/lengths/whole hashes | PASS | PASS |
| Independent Rock Ridge/Joliet + bsdtar + metadata/IDs | PASS | PASS |

Stock Fix has exactly one changed file and no Full Mod content. Full Mod matches all 609 manifest entries (607 regular files plus two directories), with no undocumented content/metadata changes. The shared decoder hash is `0f6e179f2e7fd31b5700cd0f0bbfaa4fca25b56201439c0c5b64eee96e14ca2d`. Full Mod player hash is `ab7623fb8ea21e410068a12b484fcb848eff829eaa190774c58f7d371d2913b4`.

Reproduction directories: `/home/carmine/v3-repo-reproduction-stock-2` and `/home/carmine/v3-repo-reproduction-full`. The first Stock attempt stopped before packing because unrelated official JSON has trailing commas. The corrected validator reports five byte-identical stock exceptions rather than altering them: hl_break_point_d, hl_digital_filter_d, hl_dsd_output_d, hl_play_mode_d, hl_replaygain_type_d under usr/resource/hl_json. All layouts and modified configs parse. The failed directory remains for diagnosis; no files deleted.

Historical theme SHA256 manifest passes; all historical layouts parse; shell/Python syntax passes. Old missing-reference checker initially failed on incompatible sort ordering, fixed by deterministic LC_ALL=C and sorting baseline before comm; rerun passes (38 tolerated, zero new). Its generated tracked outputs restored to original bytes after checking. No CI workflow exists in the baseline. Git whitespace check passes. Current README/build/install docs have no obsolete current v1.2 checksums/No-PEQ statements; remaining old references are historical or analytical.

Original player bounded-execution validation (six scenarios) was reviewed and retained, not broadly rerun. Fresh exact-byte patch/ELF checks and byte-identical UPT reproduction confirm the final tested patch. No new hardware flashing or RF experiment was performed.

## Evidence limitations reconciled

- **Exact JPEG trigger unknown.** No retained note/history establishes progressive versus non-progressive JPEG or exact dimensions/filesize. Documentation states reported artwork-related stability resolution from official v1.3 without guessing an encoding.
- **Volume:** actual tested final pull-down retains volume objects hidden, brightness visible. Older README/changelog claimed visible brightness+volume; current docs correct that claim while preserving historical changelog verbatim. No new slider added, no firmware contents changed.
- **Performance knobs:** exact final cache/script settings retained; no measured universal speed/stability guarantee. UBIFS sync→noatime also removes synchronous writes.
- **Bluetooth range remains unresolved**, high-rate LDAC unreliable, low-rate can cut in crowded RF, AAC reliable in observed normal-use scenarios. Wi-Fi appears poor; cause unknown. LDAC patch is a decoder correction, not a general Bluetooth or reboot fix.

## Review and publication boundary

Complete binary-aware patch (tracked changes plus all new files): `/home/carmine/v3-repo-review/REPO-V1.3-COMPLETE.diff`. Exact file inventory is in REPO-V1.3-UPDATE-PLAN.md. Checks are retained in docs/evidence/repository-validation.json and both reproduced reports; tool versions captured there too. Patch/content reviewed against exact tested manifests and documentation assertions. No tracked file deleted, original firmware overwritten, user changes discarded, tag created, commit made, push performed, public asset uploaded or release published. The publication boundary recorded here describes this local preparation snapshot, not the later public release state.

## Final release commit preparation — 2026-09-12

The user approved proceeding to commit preparation, with a final approval checkpoint before commit/tag/push/publication. Public README EN/ES, BUILD/INSTALL, NOTICE, release notes and manifest now use release-ready v1.1.0 wording. CHANGELOG release date is 2026-09-12. Release manifest uses tag/release_date rather than a proposed tag or mutable published flag. Original evidence retains historical hardware-pending fields with their superseding hardware-PASS explanation.

Final documentation-only validation passed on 2026-09-12: both original/staged/reproduced UPTs retain exact expected hashes; all 605 Full Mod source resources and Stock-only manifest remain correct; historical changelog unchanged; EN/ES coverage/table/hash parity and local links pass; historical/current source layout syntax, shell/Python syntax, historical asset/reference checks and git whitespace checks pass. No rebuild performed because firmware/build source contents did not change. HEAD remains baseline; no v1.1.0 tag; index remains unstaged. Full details are in docs/evidence/repository-validation.json.

Commit preparation files: `/home/carmine/v3-repo-review/FINAL-GIT-STATUS.txt`, `COMMIT-FILE-LIST.txt`, `PROPOSED-COMMIT-MESSAGE.txt`, `GITHUB-RELEASE-NOTES.md` and refreshed `REPO-V1.3-COMPLETE.diff`. Intended tag: v1.1.0. These are review materials; no commit/tag/push/publication executed.
