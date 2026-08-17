# Credits

This ROM is a port. Most of what you see on screen was not drawn by me, and the firmware
underneath it belongs to its manufacturers. This page says who did what, with numbers.

## Where the artwork comes from

The ROM ships **681 PNG assets**. Traced by comparing every file against the original firmware
images:

| Came from | Files |
|---|---|
| **Kae0's V3 Analog build** | **385** |
| TempoTec stock firmware (V3 Blaze and V3 Analog) | 187 |
| Modified or created for this project | 109 |

That first row says which *build* the bytes came from, not who designed them — see below.

### HiBy — the design
The look itself is HiBy's: it is the current HiBy OS interface, as shipped on the **HiBy R3 Pro II
2025**. Nobody in this chain designed it. What the rest of us did was move it between devices.

### Kae0 — brought it to the V3 Analog
[Head-Fi post](https://www.head-fi.org/threads/hiby-r3-ii-new-and-improved-physical-volume-knob-4-4mm-balanced-out-increased-power.969585/page-15#post-18600653) · 2025-03-04

Kae0 built the modified V3 Analog firmware that carried that design over, at **losber's** request,
and **385 of the assets in this ROM come from his build**.

For the record, since it is easy to get wrong: TempoTec's own V3 Analog firmware does *not* look
like this. Its interface is nearly identical to the Blaze's stock one — 604 of its files are
byte-identical. The artwork here exists in neither stock firmware.

What this project added is the second half of the journey: the Blaze runs a different SoC and a
different player binary, and a lot did not survive the move. Several defects were also present in
the V3 Analog build on its own device — the misaligned battery is visible in the thread's own
screenshots — and are corrected here. See [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md).

### losber
Asked for the V3 Analog version and supplied the stock firmware it was built from.

### TempoTec
The V3 Blaze and its firmware (`V3_ANALOG_2025`), the V3 Analog firmware, and 187 of the assets
here. Everything in this ROM outside the theme is their work, unmodified apart from five files.

HiBy also supplies everything underneath: HiBy OS, the `hiby_player` binary, the litegui
rendering engine, and the `.view` / `.dlg` layout format that all of the theming works through.

## Research and tooling this stood on

**[hiby-modding/hiby_os_crack](https://github.com/hiby-modding/hiby_os_crack)** — the `repack.sh`
that independently validated my squashfs pipeline, the R3 Pro II findings that let me confirm the
recovery mechanism on a second device before risking mine, and the X1600E datasheets.

**[Ingenic-community/Cloner](https://github.com/Ingenic-community/Cloner)** — recovery from an
erased NAND. Having this on disk is what made flashing a calculated risk instead of a gamble.

**[bidhata/Hiby-R1-Mod](https://github.com/bidhata/Hiby-R1-Mod)** — where the performance-flag
ideas came from. Most of it does not port to the Blaze: different DAC (dual AK4493 versus
CS43131) and several config flags simply do not exist in this firmware. The ones that do were
verified and adapted here.

**Tools:** squashfs-tools, xorriso, fakeroot, Pillow, Ghidra, adb, Python 3.

## Disclosure

The binary patches and build scripts here were written with AI assistance, and everything was
validated by hand on a single device. Treat it accordingly.

---

If you are Kae0, losber, or anyone else listed here and want your credit changed — reworded,
expanded, or removed — open an issue and it gets done.
