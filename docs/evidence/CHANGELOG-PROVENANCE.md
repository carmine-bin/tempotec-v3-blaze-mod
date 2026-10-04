# Changelog and credits provenance

[CHANGELOG.md](../../CHANGELOG.md) and [CREDITS.md](../../CREDITS.md) are written for users. This file keeps the audit notes that were removed from them, so the origin of historical claims stays traceable. Quoted text is reproduced verbatim from the earlier versions of those files.

## Pull-down volume slider (1.0.0 and 1.1.0)

The original 1.0.0 changelog entry listed, under "Added":

> - Brightness slider in the pull-down, working (the binary only wires it under one exact name).
> - Volume slider restored alongside it.

The 1.1.0 entry later added this audit note:

> Historical documentation below claims a restored pull-down volume slider. Artifact review establishes brightness-only in the shipped old theme and tested final port; volume objects are retained hidden in the final port. Historical entry preserved verbatim, not used as proof of shipped behavior.

The user-facing changelog now omits the volume slider from 1.0.0 "Added" and states under "Known issues" that it is not visible in current releases. The [v1.0.0 release README](../releases/v1.0.0-README.md) is kept unchanged as a historical record.

## Artwork-related instability (1.1.0)

The 1.1.0 entry credited official v1.3 stability fixes with resolving reported artwork-related instability, and added:

> The historical cover's exact JPEG encoding/dimensions/filesize are not established; no precise image condition is claimed.

## Asset provenance figures (credits)

CREDITS.md previously contained:

> Historical v1.2 documentation attributed 385 assets to Kae0's build, 187 to TempoTec stock and 109 to modifications made here. Those were reported provenance figures, not verified current counts; a later audit counted 675 PNGs in the shipped v1.2 theme. The current `[Full Mod manifest](build/v1.3/full-mod-manifest.json)` records firmware differences, not artwork authorship.

The link in that quote is shown as source because it was relative to the repository root. The manifest is at [build/v1.3/full-mod-manifest.json](../../build/v1.3/full-mod-manifest.json).
