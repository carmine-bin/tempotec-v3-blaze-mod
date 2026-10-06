# Contributing

Questions and first reports are welcome in the [Telegram group](https://t.me/V3_Blaze_Discussion). For an issue or pull request, include the device model, firmware version, reproduction steps and test method in an issue or pull request. Distinguish physical tests from static checks or simulated instruction execution.

A bind-mount over `/usr/resource` can test some layouts without flashing; reboot removes it. PNG accent tinting happens when assets load, so assess color changes from a rebuilt image. Startup configuration, fonts and cache flags also require a fresh boot.

Use one cycle per test: reboot → apply once → trigger once → inspect. Repeated live apply/revert/reparse cycles can wedge the player and leave stale render state or misleading audio symptoms.

Preserve widget names, types, parents, indexed images and duplicate-key construction order. Missing assets can be cosmetic, but malformed layouts can prevent boot. Run the established [builder](docs/BUILD.md); intentionally update the reviewed edition manifest and metadata when payload changes are authorized. Historical v1.2 resources live in [legacy/v1.2](legacy/v1.2/README.md) and use `legacy/v1.2/theme/manifest.sha256`.

For Bluetooth Receiver tests, use [tools/bluetooth](tools/bluetooth): it applies configuration in RAM, records HCI to the microSD card and reports dropped audio per run. Reboot between runs and recheck the source codec rate; Android restores adaptive LDAC after each reconnection. Do not publish captures: they contain Bluetooth addresses and audio.

Avoid boot-time polling hooks. A previous SD-mount polling hook hung startup. Keep recovery independent of the modified system.

For binary changes, record input hashes, original bytes, offsets, exact deltas and validation limits. Hardware-validated hooks must retain their tested logic during build integration.
