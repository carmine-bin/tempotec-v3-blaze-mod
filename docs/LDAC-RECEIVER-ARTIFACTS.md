# Bluetooth Receiver LDAC audio corruption in v1.3

Official TempoTec v1.3 produced digital audio artifacts in Bluetooth Receiver mode even while the LDAC stream stayed connected. Both editions correct that decoder behavior. [Link dropouts](BLUETOOTH-RANGE.md) had a different cause, corrected separately in v1.2.0.

## Hardware isolation

A controlled 330 kbps receiver capture contained approximately 3,657 consecutive A2DP/RTP packets with continuous sequence numbers and normal timestamp progression while corruption remained audible. That localized the problem beyond successful packet reception; the capture alone did not identify the decoder.

TEST 1 replaced only `/usr/lib/libldacdec.so.1` with the working v1.2 library, leaving BlueALSA, bluetoothd and the rest of v1.3 intact. The corruption disappeared on physical V3 Blaze hardware.

TEST 2 retained the original v1.3 library and bypassed only the coefficient-suppression gate described below. The corruption again disappeared. The device retained the stock interface, PEQ, Bluetooth search and official v1.3 stability behavior. Both editions use this exact correction.

## Additional downstream rule

The v1.3 `dequantizeSpectra` entry is at VA `0x3a9c`. Raw coarse/fine signed integers load at `0x3b50`/`0x3b54`; adding 3 and comparing unsigned `< 7` at `0x3b74`/`0x3b78` tests the inclusive range −3…+3:

```c
if (-3 <= coarse && coarse <= 3 && -3 <= fine && fine <= 3)
    spectrum[k] = 0.0f;
else
    spectrum[k] = (float)((double)coarse * coarse_step
                       + (double)fine * fine_step);
```

The test runs before band scaling. Small encoded integers can represent audible signal after scaling, so suppressing valid pairs changes the reconstructed spectrum.

Firmware v1.3 contains this additional downstream coefficient-suppression rule; it was not found in the public sources examined. Its author and purpose are unknown. This is a bounded source comparison, not a claim about all private SDKs or source history. [Source investigation](evidence/DECODER-ORIGIN.md).

## Exact correction

| Property | Value |
|---|---|
| File | `/usr/lib/libldacdec.so.1`, 28,804 bytes |
| Instruction offset / VA | `0x3b80` |
| Original | `10 00 40 10`, conditional branch to `0x3bc4` |
| Patched | `10 00 00 10`, unconditional branch to existing weighted-sum path |
| Changed byte | `0x3b82`: `40 → 00` |
| Delay slot | Multiply at `0x3b84`, unchanged |
| Official SHA-256 | `0427893de5def29975bc3bdf578fef32bc6e6300b73801d4813f0f918ceedb49` |
| Corrected SHA-256 | `0f6e179f2e7fd31b5700cd0f0bbfaa4fca25b56201439c0c5b64eee96e14ca2d` |

The builder checks the original/final hashes and exact byte delta. No complete decoder replacement is used in release firmware.

The v1.2 decoder uses fixed-point arithmetic; v1.3 uses a floating-point variant with different tables, allocation and initialization. BlueALSA still requests format 2, signed 16-bit PCM. Internal floating-point arithmetic does not establish a floating-point PEQ interface or a dependency between PEQ and the gate.

The public fixed-point noise/silence correction changes scale-factor handling, not this raw-coefficient test. A noise workaround remains an unconfirmed explanation. Both weighted multiplications still execute on the suppression path, so a performance motive is weakly supported and has not been benchmarked. Hardware tests establish the gate's role in the observed corruption, not its author's intent.

Evidence: [decoder patch verification](evidence/stock-fix-decoder-patch.json), [BlueALSA comparison](evidence/bluealsa-ldac-function-comparison.json), [public source inventory](evidence/ldac-public-source-manifest.json), [historical Stock verification](evidence/stock-fix-verification.json) and [current release verification](evidence/release-v1.1.2-verification.json).
