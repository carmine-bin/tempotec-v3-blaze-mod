# Notice on firmware and artwork

The `.upt` image distributed in Releases is a **modified build of TempoTec firmware for the
V3 Blaze**. It contains, essentially unchanged:

- the Linux kernel, byte-identical to TempoTec's release
- the root filesystem, in which 2677 files outside the theme are byte-identical to stock
- `hiby_player` and the HiBy OS userland

These originate from TempoTec's and HiBy's proprietary firmware and **remain their property**.
They are not covered by the MIT licence in this repository, which applies only to the original
tooling and documentation.

The graphical assets are likewise not mine to license. 385 of them come from a theme published by
Kae0, and 187 from TempoTec's stock firmware. See [CREDITS.md](CREDITS.md).

## What was actually changed

Outside the theme directories, exactly five files differ from stock, and the build verifies this
file-by-file on every run:

| File | Change |
|---|---|
| `usr/resource/set_functions.json` | two menu entries enabled (`about`, `color`) |
| `usr/resource/config_2025.json` | image and database caching enabled |
| `usr/bin/hiby_player.sh` | filesystem read-ahead and cache-pressure tuning |
| `usr/bin/mount_ubifs.sh` | `noatime` mount option |
| `usr/bin/hiby_player` | **four bytes** — one instruction replaced with a no-op |

The binary patch is documented in full, with the reasoning and the address, in
[docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md). Nothing is hidden, and
[docs/BUILD.md](docs/BUILD.md) lets you reproduce the image yourself from TempoTec's official
firmware rather than trusting the one in Releases.

## Purpose and risk

This is distributed for personal use, research, and the device-modding community. Flashing
modified firmware is done at your own risk and may void your warranty.

Not affiliated with, endorsed by, or supported by TempoTec or HiBy.

## Rights holders

If you are TempoTec, HiBy, or any other rights holder and object to the contents of this
repository, open an issue or contact me directly and I will take it down. No argument.
