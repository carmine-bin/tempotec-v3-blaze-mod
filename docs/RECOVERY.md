# Recovery — getting back if something goes wrong

Both v1.3 editions use this same recovery mechanism. Rename the selected public download to `v3_analog_2025.upt` before flashing; the `update.upt` priority warning below still applies.

Read this **before** you flash. It is short, and it is the reason flashing this player is a
calculated risk rather than a gamble.

## The one thing to know

**With the player switched off, hold `Power` + `Previous track`.**

Keep holding. The TempoTec logo appears first — **do not let go there.** Hold past it, until the
screen shows **`updater`**. Releasing at the logo just boots the player normally, which is how
most people conclude the combo does not work.

That is recovery mode. It lives in a separate part of the flash that this ROM never writes to, so
it works even if the firmware you just installed does not boot at all.

From there:

- If there is a valid `.upt` in the **root of the microSD card**, it installs it automatically.
- If there is not, it waits about 10 seconds showing that it is looking for the card, then gives
  up. Nothing is written.

No PC. No cable. No adb.

> [!NOTE]
> This combo was found by testing on the device. The bootloader exposes no button trigger in its
> strings, so it is not documented anywhere official, and combos published for other HiBy players
> do not work here. The Ingenic USB-boot mode is `Power` + `Next track`; you should not need it.

## Before you flash: set up the way back

Put a copy of the **stock** firmware on the card under a name recovery will *not* pick up
automatically, for example:

```
v3_analog_2025.upt.stock
```

If you ever need it, rename it to `v3_analog_2025.upt` and either flash from the menu or enter
recovery with the combo.

> [!WARNING]
> **Never leave a file called `update.upt` on the card.**
>
> Recovery looks for three names, in this order: the configured firmware name, the literal
> `update.upt`, and `v3_analog_2025.upt`. **`update.upt` wins.** Updating from the system menu
> also routes through recovery — so a forgotten `update.upt` gets installed instead of the file
> you just copied, and you will be certain you flashed something you did not.
>
> Keep spares under names recovery does not try, like `.upt.stock` or `.upt.bak`.

## If the player will not boot

1. Hold `Power` for 10–15 seconds to force it off. It may already be off — a black screen and a
   hung boot look the same.
2. Put a card in it with a known-good `.upt` in the root, named exactly `v3_analog_2025.upt`.
   Use the stock firmware if you are unsure.
3. With the player off, hold `Power` + `Previous track`. The logo appears on the way — keep
   holding past it, until you see **`updater`**.
4. It finds the file and flashes it on its own. Leave it alone until it reboots.

That covers a bad theme, a bad layout, a bad kernel — anything living in the main OS.

## If recovery itself will not come up

This should not happen from flashing a ROM. Nothing here writes to the bootloader or the recovery
partition, and the build verifies the kernel is passed through byte-identical to TempoTec's.

If it does, the last resort is the Ingenic USB boot ROM, which loads code over USB before any
flash content is read. The tool is
[Ingenic-community/Cloner](https://github.com/Ingenic-community/Cloner), and it can rewrite the
whole NAND from an erased state. Entry is `Power` + `Next track`.

You will need the factory `.ingenic` image, which ships inside TempoTec's official firmware zip.
This path is documented by Ingenic but has not been exercised on this device — if you get here,
open an issue before improvising.

## How the partitions are laid out

Useful if you are modifying firmware rather than rescuing a player:

| Partition | Contents |
|---|---|
| `mtd0` | u-boot (512 K) |
| `mtd1` / `mtd2` | main kernel (5 M) and root filesystem (45 M) — what this ROM replaces |
| `mtd3` / `mtd4` | recovery kernel (5 M) and root filesystem (24 M) — **untouched** |
| `mtd5` | boot selector and boot-logo flag (512 K) |
| `mtd6` | user data (45 M, UBIFS) |

u-boot reads `mtd5` to choose which pair to boot: `ota:kernel` for the main system, `ota:kernel2`
for recovery. The vendor's own updater writes it by partition *name*, never touching the
bootloader, and flips the selector back when it finishes. That is why a failed main-system flash
still leaves you a working recovery.
