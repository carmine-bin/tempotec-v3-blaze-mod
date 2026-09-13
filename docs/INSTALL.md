# Installing, step by step

The short version lives in the [README](../README.md). This is the long one, for anyone who has
never flashed a player before.

Nothing here needs a PC beyond copying a file to a memory card.

## 0. Check you have the right device

This ROM is **only** for the **TempoTec V3 Blaze**.

Confusingly, the Blaze's firmware calls itself `V3_ANALOG_2025`. That is this device. The older
**TempoTec V3 Analog** is a different player with a different chip — this image will not work on
it, and you should not try.

The device must be the V3 Blaze (`V3_ANALOG_2025`). Both current editions are based on official v1.3 and use the same updater. About is enabled by Full Mod; Stock Fix preserves stock menu behavior.

## 1. Know how to get out before you go in

Read [RECOVERY.md](RECOVERY.md) now, not later. It is short.

The important part: the V3 Blaze has a recovery mode reached by a **key combo**, and it lives in
a separate part of the flash that this ROM never touches. If a flash goes wrong, you hold two
buttons and reinstall a firmware file from the card. It does not depend on adb, a cable, or
anything this ROM installed.

That is why flashing this is a calculated risk rather than a gamble. But read it first.

## 2. Keep a way back

Before flashing, put a copy of the **stock** firmware on the same card under a different name,
for example `v3_analog_2025.upt.stock`.

TempoTec publishes it on their download page. If you ever want to go back — or something goes
wrong — you rename that file to `v3_analog_2025.upt` and run the same update procedure.

Rolling back is exactly as easy as installing. That is worth setting up while everything is calm.

> [!WARNING]
> **Do not name that spare `update.upt`.**
>
> Recovery tries three filenames and the literal `update.upt` outranks `v3_analog_2025.upt`.
> Updating from the system menu goes through recovery too, so a leftover `update.upt` gets
> installed instead of the file you just copied — and everything will look like it worked.
> Use a suffix recovery ignores, like `.upt.stock`.

## 3. Download and verify

Choose `V3-Blaze-v1.3-Stock-LDAC-Fix.upt` or `V3-Blaze-v1.3-Full-Mod.upt` from [Releases v1.1.0](https://github.com/carmine-bin/tempotec-v3-blaze-mod/releases/tag/v1.1.0). Check SHA-256 against the [README table](../README.md#install) or accompanying `SHA256SUMS`:

```bash
sha256sum V3-Blaze-v1.3-Stock-LDAC-Fix.upt
sha256sum V3-Blaze-v1.3-Full-Mod.upt
```

On Windows use `certutil -hashfile <downloaded-file> SHA256`. If it does not match, stop. **Rename whichever edition you choose to exactly `v3_analog_2025.upt` before copying it to the card.** Renaming does not change firmware contents.

## 4. Copy it to the card

Put the file in the **root** of a microSD card — the top level, not inside a folder.

The filename must be exactly:

```
v3_analog_2025.upt
```

The player looks for that specific name and ignores everything else. If your system hides file
extensions, make sure you have not ended up with `v3_analog_2025.upt.upt`.

Eject the card properly, then put it in the player.

## 5. Flash

On the player:

**Settings → Firmware update → Update via micro SD card**

Confirm. From here it is automatic:

1. The player writes a boot flag and reboots.
2. It comes up in recovery — a plain screen, no theme.
3. Recovery mounts the file from the card and writes it to flash.
4. It reboots into the new firmware.

**Do not power it off, unplug it, or press buttons while this runs.** It takes a couple of
minutes.

Database/settings behavior can depend on existing persistent state; do not interrupt the initial boot.

## 6. Check it worked

Both editions should boot normally, preserve official v1.3 PEQ/search functionality and provide clean LDAC without the digital corruption. Full Mod additionally has the custom launcher/Now Playing, About/colour-theme access and a working brightness slider; its pull-down volume objects are hidden. Stock Fix retains stock UI behavior. Bluetooth range/interference is still [unresolved](BLUETOOTH-RANGE.md).

If the player will not boot, go to [RECOVERY.md](RECOVERY.md).

## Going back to stock

Rename your stock `.upt` back to `v3_analog_2025.upt` and repeat step 5. Nothing about this ROM
makes returning harder, and it does not touch the bootloader or the recovery partition.
