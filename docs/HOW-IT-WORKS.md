# How it works

Notes from porting a theme between two players that look similar and are not. Written for the
next person who opens a `.view` file and wonders why renaming something broke it.

## The short version

HiBy OS draws its interface with an engine called litegui. Layouts are JSON files describing
elements by name and position; artwork is loose PNGs. Both live in the read-only root filesystem,
so "installing a theme" means rebuilding the firmware image.

That part is mechanical. The interesting part is that **the layout is not data the binary reads
generically — it is an interface the binary expects you to implement.**

## The element name is the API

The clearest example is the brightness slider.

The V3 Analog theme has a brightness control in its pull-down menu. Ported to the Blaze it
rendered, it dragged, and it did absolutely nothing. The obvious conclusion — the Blaze's binary
doesn't support it — was wrong, and cost a couple of days.

Disassembling the pull-down builder shows the binary matching element names against string
literals, installing a callback for each one it recognises. It matches `pull_down_menu_pb`. The
donor theme called the element `pull_down_menu_bklight_pb`. Same widget, same geometry, one
unrecognised name, so the callback was never installed and the slider was inert.

Renamed to `pull_down_menu_pb`, brightness works.

The same lookup logic explains a crash. Opening the USB DAC screen froze the player and rebooted
it. Its builder walks a fixed array of six element names and dereferences each lookup **without a
null check** — and the load sits in the delay slot of the following `jal`, which is why a
scripted scan for unguarded dereferences misses it and you have to decode the instruction by
hand. Two of the six names were absent from the ported layout, so the fourth iteration
dereferenced null before drawing anything.

Practical rules that fell out of this:

- An element's **name** determines whether it is wired up. Renaming is not cosmetic.
- Its **type** matters: the global lookup is by name *and* JSON type. An `imageview` where the
  binary wants a `numview` fails silently.
- Its **parent** matters. One lookup used here is non-recursive — it only searches direct
  children — so an element under the wrong parent dies quietly, with no crash to tell you.
- A missing PNG is harmless; the stock firmware already ships 38 dangling references and boots
  fine. Malformed layout **syntax** is what causes boot loops.

## The battery, or: read the engine before you redraw the art

The battery icon lost its fill below roughly 30% charge, and on the charging screen it showed a
second battery inside the first.

Two device tests pinned the engine's behaviour: it takes the **first `h × pct` rows** of the fill
image and draws them **pinned to the bottom** of the element, at `y + h - h×pct`. It does not
scale, and it does not centre.

That rule is fine if the fill image is exactly the fill. The donor artwork was a whole battery —
outline, terminal cap and all — so cropping the top 59% of it and sliding it down put *its own
cap* halfway up the frame. The result reads unmistakably as two batteries:

```
frame (static)        fill image, 59% cropped     what you see
┌─▄─┐                 ┌─▄─┐                       ┌─▄─┐
│   │        +        │███│  slid down     =      │   │
│   │                 │███│                       │ ▄ │   ← the fill image's own cap
└───┘                 └───┘                       │███│
```

The fix is to make the element the binary drives **exactly the opening in the frame**: a solid
fill sized to the hole, positioned at the hole, with the frame drawn as a separate static image
under a name the binary does not know. Then the percentage crop maps linearly and can never
escape.

This is not a defect introduced by porting. The same artwork produces the same misplaced battery
on the V3 Analog it was made for — it is visible in the original thread's screenshots. The engine
is the same on both devices; the defect travels with the asset.

### Verifying it without the device

The engine's rule is simple enough to reimplement in ten lines, which makes the fix testable on a
laptop: crop the first `h × pct` rows, composite at `y + h - h×pct`, render at 100/59/25/10%.
Doing that reproduced the reported photo exactly at 59%, then showed a clean fill afterwards.

Worth the effort. Every device test on this player costs a reboot, and reboots are where mistakes
compound.

## Off-by-one states

The Blaze cycles **three** gain levels. The donor player had two. Every ported gain control
therefore lost its middle state — the pull-down icon, the settings switch — and showed nothing
when gain was medium, because index 1 pointed at an image that did not exist.

This same shape recurred three separate times (gain, the PEQ switch, and a settings toggle),
always as an element indexed `img_path_N` where `N` runs over a state count the binary decides.
When porting between HiBy devices, **count the states before trusting an indexed control.**

## Four bytes (historical v1.2 patch)

Enabling the image cache made the player report degraded playback quality — a bitrate readout
that no longer matched the file.

The cache is not the culprit; it is a trigger. Turning it on changes which code path runs when a
track loads, and one of those paths calls a routine that parses metadata from *the next file in
the list* into a shared struct — overwriting the current track's title, artist, album and format
fields. It also leaks: the routine begins with a `memset` of the struct without freeing the
string pointers already there.

The only two callers of the relevant API read the path out of the returned struct and never touch
the global afterwards, so the parse is dead work with a destructive side effect. Replacing the
call with a no-op fixes the quality readout and removes a full open-and-parse per track change.

```
vaddr        0x00436a00      jal FUN_00435060   →   nop
file offset  0x00036a00      (0x436a00 - 0x400000)
```

Four bytes. The build asserts that the shipped binary differs from stock in **exactly** those
four and nothing else.

## Tinting, and why the theme colours kept lying

Assets do not necessarily render in the colours they are drawn in. The firmware's accent picker
repaints PNGs at load time, and `litegui/theme1/no_skin_list.txt` is the opt-out list. Anything
absent from that list gets tinted.

That single file explains an entire family of "the colour is wrong" bugs, in both directions —
the volume bar not following the accent (missing from the list), the colour picker's own swatches
repainting themselves, QR codes getting tinted until they no longer scanned.

Two traps worth knowing:

- Tinting happens **when the PNG is loaded**, so it cannot be evaluated with a live bind-mount —
  the mount lands after the player has already loaded its images. Only a baked image tells the
  truth.
- The list uses Windows-style paths and **CRLF** line endings. Preserve them.

## How the historical v1.2 build kept itself honest

Rebuilding a root filesystem by hand is easy to get subtly wrong, and the failure mode is a
device that does not boot. The build runs four gates and refuses to produce an image if any fail:

1. **Staging manifest** — every theme file checked against a recorded SHA-256 before anything is
   packed. An accidental edit stops the build instead of shipping.
2. **JSON syntax** on all 149 layout files. Malformed layout is the one thing that reliably
   causes a boot loop.
3. **Metadata diff** against the stock filesystem — modes, owners, sizes. The whole round-trip
   runs under `fakeroot`, because unpacking as a normal user silently drops the setuid bit on
   `busybox` and the image will not boot.
4. **Content diff**, SHA-256 per file: 2677 files outside the theme must be byte-identical to
   stock, and the five that differ must differ in exactly the expected way — including the
   binary, byte-counted.

The kernel is passed through untouched and its checksum compared against TempoTec's manifest.

## Things that stayed broken

- **PEQ is now included in official v1.3** and preserved in both editions. The earlier v1.2 investigation established 29 element names and a hardcoded 2×5 band grid, but did not have working processing.
- **Two pull-down controls** the binary draws but never listens to. Hidden rather than left as
  dead widgets.

## Tools

`xref.py` (cross-references including `lui`/`addiu` pairs, which a naive scan misses),
`mipsdis.py`, `annotate.py` (disassembly annotated with string pointers), `lookup-audit.py`
(finds unguarded dereferences after name lookups, delay slots included), and Ghidra headless for
decompilation. All in [`../build/scripts`](../build/scripts).

## Migration to official v1.3

Official v1.3 is the complete base for both current editions, including PEQ, real-time Bluetooth search and TempoTec's stability fixes. It changes 208 non-timestamp paths from v1.2, including player/server, Bluetooth, kernel/modules, USB and supporting resources. Overlaying the old rootfs or replacing whole theme directories would risk rolling back functional fixes or dropping v1.3-only resources. No old Bluetooth/audio/kernel/system components were copied over.

Full Mod ports an explicit allowlist of layouts/assets and exact configuration/script deltas. All 151 official layouts remain, including byte-identical PEQ/filter layouts. Duplicate JSON object keys are preserved with ordered pairs: repeated widget-type keys and construction-marker order are meaningful to this renderer. The final merge preserves 1,283 official named widget/type/parent contracts. The final launcher image fallback, play/pause state mapping and notice first-child text behavior were corrected after intermediate hardware tests exposed their defects. The user subsequently confirmed that this exact final image worked successfully on physical hardware.

The old v1.2 player offset cannot be reused. In v1.3 the patch is at **file offset `0x38240`, VA `0x438240`**: `08 da 10 0c → 00 00 00 00`, removing `jal 0x436820`. The next-track API output structure (`0xa88` bytes) is copied first. The removed parse would write next-track metadata into the shared current-track buffer at `0x988f90`; API operation 4 reads that buffer. The identified operation-`0x1f` callers use the returned path at buffer+4. Output copy, selection restoration, unlock/return path and `addiu a0,a0,4` delay slot remain unchanged. The old `0x36a00` offset is not modified.

Validation used actual v1.3 MIPS bytes, disassembly, callsite inspection, exact original/final hashes and bounded instruction execution with external calls mocked. Six cases passed: valid next-track output, null output, absent next track, absent lock callback and API 4 with/without output. This proves isolated logic, not every indirect caller or the complete player pipeline. The final binary differs in exactly four bytes; ELF layout/import/export/relocation output remains unchanged. See [player validation](evidence/full-mod-player-validation.json) and [complete file manifest](../build/v1.3/full-mod-manifest.json).

Both editions independently apply the **same TEST 2 decoder correction**, a single changed byte in the v1.3 LDAC decoder. It has no demonstrated dependency on the theme, custom player patch or PEQ. Stock Fix changes no other filesystem content. See [LDAC-REGRESSION.md](LDAC-REGRESSION.md) for exact gate semantics and hardware isolation; [BLUETOOTH-RANGE.md](BLUETOOTH-RANGE.md) covers the separate unresolved RF symptom.

The final pull-down intentionally preserves brightness only; official volume/decorative lookup objects are hidden. Earlier documentation claiming two visible sliders was inaccurate. Full Mod's exact cache/script settings are recorded in the manifest and README; the UBIFS substitution removes synchronous writes as well as adding noatime. Do not infer a quantified v1.3 speed or stability benefit from inclusion alone.

The current builder supplies ownership, permissions, special bits, timestamps and links explicitly through a numeric-owner TAR rather than trusting unprivileged extraction. It validates the rebuilt and re-extracted filesystem against the manifest and optionally against the exact tested UPT. See [BUILD.md](BUILD.md). Historical v1.2 gates/counts above remain documentation of the earlier implementation.
