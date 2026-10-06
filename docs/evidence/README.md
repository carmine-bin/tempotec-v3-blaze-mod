# Technical evidence

Firmware and component hashes identify the audited artifacts. Published v1.1.0 and v1.1.2 records remain unchanged; current v1.2.0 results are separate.

- [v1.2.0 verification](release-v1.2.0-verification.json): both editions, deterministic rebuild and the single filesystem difference from v1.1.2 (`etc/bluetooth/main.conf`).
- [Bluetooth Receiver measurements](bluetooth-receiver-airtime.json): HCI scan parameters observed on official v1.3, method, per-run rate/dropped audio/link quality and the alternatives that did not help.
- [v1.1.2 verification](release-v1.1.2-verification.json): rebuilt Stock and Full Mod, exact reference equivalence, six UI payload changes and protected components.
- [Validated UI investigation](../UI-FIXES.md): root causes, dispatch audit, hook addresses and validation limits.

- [Decoder origin investigation](DECODER-ORIGIN.md): inspected decoder variants, public source history and the uncertain origin/purpose of the downstream coefficient gate. TEST 1 and TEST 2 identify the hardware decoder experiments described in [LDAC receiver artifacts](../LDAC-RECEIVER-ARTIFACTS.md).
- [Stock + LDAC Fix verification](stock-fix-verification.json) (v1.1.0, before the rename to Stock + Fixes): release hashes, ISO/OTA checks, the decoder-only filesystem change, permissions/ownership/timestamps, links, rootfs metadata and physical-device validation.
- [Full Mod verification](full-mod-verification.json): container/kernel/filesystem checks, final UI/resource and protected-component audit, decoder/player patch details and release hashes. Automated verification is distinguished from subsequent physical V3 Blaze validation.
- [Reproducibility](reproducibility-v1.1.0.json): both independent rebuilds matched the tested release UPT bytes and SHA-256. Detailed container, filesystem, layout and reference comparisons are retained. [Tool versions](build-tool-versions.json) identify the recorded environment.
- [Decoder patch validation](stock-fix-decoder-patch.json) and [player patch validation](full-mod-player-validation.json): exact binary offsets/bytes, hashes, validation method and limits.
- [Final UI correction record](full-mod-CORRECTION-MANIFEST.json): scoped resource corrections and their technical justification.
- [BlueALSA instruction comparison](bluealsa-ldac-function-comparison.json) and [public LDAC source inventory](ldac-public-source-manifest.json): portable caller-comparison and source revision/fork evidence.
- [Repository validation](repository-validation.json): lasting artifact, source-resource, documentation and syntax check results; not a publication checkpoint.
- [Changelog and credits provenance](CHANGELOG-PROVENANCE.md): audit notes on historical changelog and credits claims (pull-down volume slider, artwork instability, asset counts).

Canonical edition filesystem manifests live in [build/v1.3](../../build/v1.3/): [Stock Fix](../../build/v1.3/stock-fix-manifest.json) and [Full Mod](../../build/v1.3/full-mod-manifest.json). Redundant evidence copies and the TSV rendering are omitted; the canonical JSON preserves paths, hashes, permissions, owners and reasons.

The [Bluetooth Receiver dropouts](../BLUETOOTH-RANGE.md) have a separate cause from the decoder corruption. Firmware and visual assets retain their original rights holders.
