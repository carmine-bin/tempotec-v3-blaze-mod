# Legacy v1.2 generation

This directory holds the generation of the mod based on official TempoTec firmware v1.2 (`V3_ANALOG_2025`, build `202601301221`), which produced project release v1.0.0.

The current builder ([build/build-v1.3.py](../../build/build-v1.3.py), described in [Build](../../docs/BUILD.md)) does not use anything here. It is kept as a record of how v1.0.0 was made and where the Full Mod artwork and binary findings came from.

| Path | Contents |
|---|---|
| `theme/theme_port/` | Staged v1.2 theme (`litegui/theme1` and `layout/theme1`) |
| `theme/manifest.sha256` | SHA-256 manifest of the staged theme, checked by the old builder |
| `theme/baseline-missing-refs.txt`, `theme/missing-refs.txt` | Missing PNG references in stock and in the staged theme |
| `build/build-upt-v3.sh` | Old v1.2 builder; requires `BUILD_HISTORICAL_V12=1` |
| `build/scripts/` | Asset helpers that produced the staged theme, plus reverse-engineering helpers (`xref.py`, `mipsdis.py`, `annotate.py`, `lookup-audit.py`) |

The relative layout matches the original repository root, so the scripts resolve their paths from this directory. Two unreferenced PNG files left over from the donor artwork were removed from `theme/theme_port/litegui/theme1/stream_media/` after v1.0.0, and the manifest was updated to match.

See the [v1.0.0 build record](../../docs/releases/v1.0.0-BUILD.md) and the [v1.0.0 release notes](../../docs/releases/v1.0.0-README.md).
