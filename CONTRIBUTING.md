# Contributing

Small project, few rules, but the ones here exist because ignoring them cost me time or a
reboot loop.

## Test without flashing where you can

Most theme work can be validated with a bind-mount over `/usr/resource` on a running device —
no flashing, revert by rebooting. Two things it **cannot** tell you:

- **Anything about colour.** Accent tinting is applied when a PNG is loaded, and the bind lands
  after the player has loaded its images. Colour must be judged from a baked image.
- **Anything in the boot path.** Config files, fonts and cache flags are read once at startup.

## Do not iterate on a hot player

The player wedges if you apply, revert and re-parse repeatedly while it runs: CPU spins, the
render cache goes stale, audio dies, and you get diagnostics that are simply false. More than one
wrong conclusion in this project came from that.

**One cycle = reboot → one apply → one trigger → test.** Slower, and much faster overall.

## Rebuild the manifest

After regenerating any staged asset, rebuild `manifest.sha256` before applying or building.
The build refuses to run on a manifest mismatch — that is the point, but it means a stale
manifest looks like corruption.

## Layout syntax is the dangerous part

A missing PNG is cosmetic; the stock firmware already ships 38 dangling references. **Malformed
layout JSON is what causes a boot loop.** The build gates all 149 layout files, so let it.

Renaming an element is never cosmetic — see [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md).

## Boot hooks

Don't add one. An earlier version shipped an init hook that polled for the SD card mount while
the system was mounting it, and hung the boot. Recovery is a key combo that depends on nothing
baked into the ROM; keep it that way.

## Before opening a PR

Say which device and firmware version you tested on, and whether you flashed or used a
bind-mount. "Works on mine" without the version is not useful here.
