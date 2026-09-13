# Technical evidence

This directory contains the curated evidence supporting the v1.1.0 firmware editions. Firmware and component hashes identify artifacts independently of their storage location.

- [Decoder origin investigation](DECODER-ORIGIN.md): inspected decoder variants, public source history and the uncertain origin/purpose of the downstream coefficient gate. TEST 1 and TEST 2 identify the hardware decoder experiments described in [LDAC-REGRESSION.md](../LDAC-REGRESSION.md).
- [Stock + LDAC Fix verification](stock-fix-verification.json): release hashes, ISO/OTA checks, the decoder-only filesystem change, permissions/ownership/timestamps, links, rootfs metadata and physical-device validation.
- [Full Mod verification](full-mod-verification.json): container/kernel/filesystem checks, final UI/resource and protected-component audit, decoder/player patch details and release hashes. Automated verification is distinguished from subsequent physical V3 Blaze validation.
- [Reproducibility](reproducibility-v1.1.0.json): both independent rebuilds matched the tested release UPT bytes and SHA-256. Detailed container, filesystem, layout and reference comparisons are retained. [Tool versions](build-tool-versions.json) identify the recorded environment.
- [Decoder patch validation](stock-fix-decoder-patch.json) and [player patch validation](full-mod-player-validation.json): exact binary offsets/bytes, hashes, validation method and limits.
- [Final UI correction record](full-mod-CORRECTION-MANIFEST.json): scoped resource corrections and their technical justification.
- [BlueALSA instruction comparison](bluealsa-ldac-function-comparison.json) and [public LDAC source inventory](ldac-public-source-manifest.json): portable caller-comparison and source revision/fork evidence.
- [Repository validation](repository-validation.json): lasting artifact, source-resource, documentation and syntax check results; not a publication checkpoint.

Canonical edition filesystem manifests live in [build/v1.3](../../build/v1.3/): [Stock Fix](../../build/v1.3/stock-fix-manifest.json) and [Full Mod](../../build/v1.3/full-mod-manifest.json). Redundant evidence copies and the TSV rendering are omitted; the canonical JSON preserves paths, hashes, permissions, owners and reasons.

Physical hardware validation does not resolve the separate [Bluetooth range/interference issue](../BLUETOOTH-RANGE.md). No proprietary player or decoder executable is committed. Firmware and visual assets retain their original rights holders.
