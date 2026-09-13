# Origin of the firmware 1.3 LDAC coefficient gate

Investigation completed 2026-09-11. TEST 1 and TEST 2 passed physical V3 Blaze hardware validation. The origin assessment uses binary/source comparison and the recorded decoder experiments.

## Assessment

The strongest explanation supported by the binary/source comparison is a change from a fixed-point decoder variant to a floating-point variant, with an additional coefficient-suppression modification absent from the inspected public source. The gate looks like a crude noise/silence suppression rule. Its purpose and author cannot be established from these binaries.

There is no demonstrated technical dependency between the gate and PEQ. A direct performance optimization is poorly supported by the actual instructions. Neither the gate nor the complete 1.3 library can be identified as a straightforward update to the latest inspected public decoder revision. A vendor or SDK integration change could have brought the floating decoder and PEQ into the same release, but that organizational connection remains unknown.

## Confirmed binary findings

| Area | Firmware 1.2 | Firmware 1.3 | Implication |
|---|---|---|---|
| Spectral reconstruction | Fixed-point weighted coarse/fine sum | Floating-point reconstruction plus raw-integer −3…+3 gate | Semantic change, not just recompilation |
| Dequantizer comparisons | Maintains min/max diagnostics for coarse, fine and sum | Tests each encoded value against the small-value range | Old comparisons do not clip coefficients and are not an earlier gate |
| Transform | Fixed-point tables and integer arithmetic | Float buffers, double tables/intermediates | Broader implementation change surrounding the gate |
| Scale-factor index zero | Scaling still performed | `scaleSpectrum` skips scaling when index is zero | Matches a known difference between public variants |
| Handle allocation | `calloc` | `malloc` | Another source-level behavior difference |
| Wrong processing mode at initialization | Reinitializes decoder | Rejects mode | Does not look like a monotonic adoption of newer initialization fixes |
| BlueALSA output request | Format 2, signed 16-bit PCM | Same | Internal floating-point arithmetic does not establish a new floating-point PEQ interface |

Original decoder hashes remain:

```text
1.2 3889bca33fde5da1c1cf3630fd19de2811d6d6227ccc77ee621be606d1d3ff3b
1.3 0427893de5def29975bc3bdf578fef32bc6e6300b73801d4813f0f918ceedb49
```

### Surrounding decoder logic and call sites

The ordinary decoding sequence remains coarse spectrum decoding, fine/residual spectrum decoding, dequantization, band scaling, IMDCT, and PCM conversion. In 1.3 `ldacDecode_type` (entry `0x1e68`), the indirect call sites are:

| Call-site VA | Target |
|---|---|
| `0x21b4` | `decodeSpectrum` |
| `0x21c8` | `decodeSpectrumFine` |
| `0x21d8` | `dequantizeSpectra` |
| `0x21e8` | `scaleSpectrum` |
| `0x2204` | `RunImdct` |

The untyped decode entry also uses the same dequantizer. The gate is in the normal per-channel reconstruction path; it is not conditioned on PEQ enablement, user gain, Q, frequency, Bluetooth search, packet loss, or an error/recovery state. There is no bitrate check at the gate.

The 1.2 dequantizer begins at `0x333c`; its weighted integer arithmetic and diagnostic min/max updates are followed by `scaleSpectrum` at `0x356c`. The 1.3 dequantizer begins at `0x3a9c`; `scaleSpectrum` begins at `0x3be0`, with the zero-scale-factor skip at `0x3c1c`.

In 1.3, raw coarse/fine integers are loaded at `0x3b50`/`0x3b54`. Adding 3 and testing unsigned `< 7` implements inclusive −3…+3. Both weighted multiplications execute (`0x3b7c` and branch delay slot `0x3b84`) even on the zero-output path. The gate avoids the final addition and conversion, but does not avoid bitstream parsing, the coefficient loops, scaling or IMDCT. It adds range tests and branches. No device benchmark establishes a speed benefit.

The retained [BlueALSA comparison](bluealsa-ldac-function-comparison.json) shows the same aligned 1,268-byte LDAC receiver-thread instruction sequence, apart from relocated call/address operands: entry `0x41a8bc` in 1.2, `0x41a9dc` in 1.3. This establishes unchanged local control flow, not equivalence of every called function. In 1.3 the decoder call is at `0x41ad80`, with format 2 set at `0x41ad7c`; PCM scaling and writing follow at `0x41addc` and `0x41adec`. Their targets are `io_pcm_scale` at `0x414e64` and `io_pcm_write` at `0x4151f4`.

### PEQ comparison

Both player binaries already contain PEQ-related UI/parameter strings, `/data/peq`, and the name `PEQ Combined`. This demonstrates pre-existing code/scaffolding in 1.2; it does not prove that the released 1.2 UI exposed working PEQ.

Firmware 1.3 adds PEQ module lifecycle strings and settings material, including `PEQ Combined module init`, `PEQ Combined module done`, and `peqc`. The initialization text is referenced by actual player code at `0x63d104`, followed by an indirect callback at `0x63d108`. This is evidence of player-side integration work, not merely an unused filename. It does not by itself establish which playback modes execute every PEQ operation.

The player constructs the ALSA device name `bluealsa:DEV=%s` in both versions (string reference at `0x47e0f8` in 1.2 and `0x480fd8` in 1.3). It imports ALSA PCM functions. It does not list `libldacdec` as a dynamic dependency. The decoder lists only `libm` and `libc` as needed libraries and contains no identified PEQ configuration interface. Together with the unchanged signed-16-bit producer call, these findings place the observed PEQ integration separately from LDAC spectral reconstruction. A complete runtime trace of all player processing routes was not performed.

TEST 2 is particularly useful here: all other 1.3 code, including its PEQ-related implementation, remained in place while the gate-only bypass removed the reported artifacts. That supports independence of this regression from a required PEQ implementation change. It does not certify every PEQ setting or the unrelated crash fixes.

## Public source comparison

The firmware has strong structural correspondence with the community `hegdi/libldacdec` family and its `anonymix007` fixed-point variant. Matching source filenames alone would be weak evidence; the distinctive min/max instrumentation, arithmetic representations, table layouts and initialization behavior make the correspondence substantially stronger. This identifies a source family, not an exact vendor commit or a verified Sony source release.

Sources retained locally:

| Repository/ref | Inspected commit |
|---|---|
| hegdi master | `7f3bd6cc1586b764b02f2e4f20b16c7ff18758b9` |
| anonymix007 master | `c90094b15e25aef0e47c6d775fa94aceb36cabbc` |
| anonymix007 fixedpoint | `61509f05e9ea63e6c1747cf4f409550028bc3b1b` |

The public floating dequantizer forms a weighted sum without the gate. The fixed-point branch also forms the sum without the gate, and contains the distinctive min/max diagnostic variables seen in firmware 1.2. Firmware 1.3 resembles the floating implementation, but exact source identity is not claimed; arithmetic precision details and downstream edits can differ. See the pinned [floating spectrum source](https://github.com/hegdi/libldacdec/blob/7f3bd6cc1586b764b02f2e4f20b16c7ff18758b9/spectrum.c) and [fixed-point spectrum source](https://github.com/anonymix007/libldacdec/blob/61509f05e9ea63e6c1747cf4f409550028bc3b1b/spectrum.c).

The reachable spectrum-file history in both cloned repositories contains no identified equivalent gate. Fifteen additional fork default-branch `spectrum.c` snapshots are byte-identical to one another and contain the ungated weighted sum. The fork list, snapshots, hashes and source history patches are retained under `origin-research/`. This is a bounded negative finding: private SDK branches, deleted history and all other LDAC implementations were not exhaustively surveyed. It does not prove that TempoTec itself authored the change.

Two public changes help distinguish the variants:

1. Commit [`efd4e3d…`](https://github.com/anonymix007/libldacdec/commit/efd4e3d8e156c38dec625eba338cf5a6806f82ae), titled “Fix noise-instead-of-silence issue”, removes the positive-scale-factor guard in the **fixed-point** scaling path. Firmware 1.2 has the resulting behavior. Firmware 1.3 retains the floating path's guard. This commit changes scaling, **not** the −3…+3 gate.
2. Commit [`52ed47c…`](https://github.com/anonymix007/libldacdec/commit/52ed47c1c6ac103ee2d9fa67d7f9e475e93108e4) changes allocation to `calloc` and introduces wrong-mode reinitialization. Firmware 1.2 exhibits those behaviors; 1.3 exhibits the earlier malloc/rejection behavior. Consequently, calling 1.3 a straightforward upgrade to the latest inspected public decoder is unsupported. Commit dates do not date the vendor's source snapshot or firmware build.

## Hypotheses, ranked by supporting evidence

| Explanation | Assessment |
|---|---|
| Downstream noise/silence suppression added while changing decoder variants | Most plausible purpose from the gate's behavior, but unconfirmed. It explicitly suppresses small values. The related public silence fix and changed zero-scale handling provide a concrete possible motivation. |
| Broader SDK/audio integration change accompanying PEQ | Plausible explanation for why a different decoder was bundled in the same release. No source history or call dependency proves that PEQ motivated either the variant switch or gate. |
| CPU optimization | Weak support. Both multiplications and the expensive surrounding work still run; tests and branches are added. No benchmark was performed. |
| Code-size optimization or simplification | Possible motive for the wider variant change: the library shrinks from 42,488 to 28,804 bytes. This cannot explain the gate specifically; double tables and runtime storage grow, so smaller file size is not a general memory optimization. |
| Routine upstream decoder update | Public source ancestry is strongly supported; upstream origin of this gate is not. The gate is absent from the inspected sources/history, and some 1.3 behavior resembles older floating code. |
| Aging/freezing/crash fix or Bluetooth search | No supporting linkage. This gate neither validates buffers nor handles recovery, allocations or discovery. An undocumented shared vendor change remains possible, but the changelog cannot establish it. |

The noise-workaround hypothesis has an important limitation: the gate tests raw coefficient integers, not scale-factor zero. It therefore cannot be equated to the public silence fix. Small encoded values can become substantial audio after band scaling, which explains why this rule can discard legitimate signal. Hardware PASS establishes the causal regression for the tested symptom, not the author's motivation.

## Evidence and limitations

- [LDAC investigation](../LDAC-REGRESSION.md): exact gate semantics, controlled capture conclusions and hardware decoder isolation.
- [BlueALSA instruction comparison](bluealsa-ldac-function-comparison.json): aligned receiver-thread code differences.
- [Public source revision inventory](ldac-public-source-manifest.json): inspected revisions/history, fork snapshot hashes and original decoder hashes.
- [Decoder patch verification](stock-fix-decoder-patch.json) and [release manifest](../releases/release-manifest.json): exact correction and reference artifact hashes.

The upstream commit links above identify the public noise/silence and initialization changes. Determining the downstream gate's actual rationale would require a vendor/SDK source diff or the original author's explanation; its purpose and author remain unknown.
