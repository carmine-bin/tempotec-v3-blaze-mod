# LDAC regression in firmware v1.3

**Status: decoder corruption fixed; hardware-confirmed in both editions.** Bluetooth range/interference remains [unresolved](BLUETOOTH-RANGE.md).

## Observable problem and receiver capture

Official TempoTec v1.3 introduced severe digital/electronic corruption during affected LDAC playback. The Bluetooth stream could remain connected while the audio was corrupt. The working v1.2 decoder did not exhibit this specific symptom.

In the controlled v1.3 LDAC 330 kbps btmon/HCI capture, approximately **3,657 consecutive A2DP/RTP media packets** arrived. RTP sequence numbers remained continuous, with no sequence gaps; timestamps advanced normally, without abnormal discontinuities during that run. Audible corruption remained present. Capture continuity strongly localized the problem after successful packet reception, toward the receiver-side decode/audio path rather than simple RF packet loss. Continuity alone was not proof of the responsible component; the isolated hardware tests supplied that proof.

## TEST 1: isolate the decoder

TEST 1 kept official v1.3 and replaced only `/usr/lib/libldacdec.so.1` with the working v1.2 decoder. BlueALSA, bluetoothd and the rest remained v1.3. On actual V3 Blaze hardware the digital corruption disappeared, isolating the decoder as the responsible component.

Binary analysis established that v1.2 uses a fixed-point decoder variant and v1.3 a floating-point variant. Arithmetic, tables, allocation and initialization changed. BlueALSA still ultimately requests format selector `2`, signed 16-bit PCM. Internal floating-point arithmetic does not imply a floating-point PEQ interface. There is no demonstrated dependency between this decoder change and PEQ.

## The additional downstream gate

In v1.3 `dequantizeSpectra` begins at ELF virtual address `0x3a9c`. Coarse and fine signed integers are loaded at `0x3b50`/`0x3b54`. Each has 3 added and is compared **unsigned `< 7`** at `0x3b74`/`0x3b78`. For ordinary decoded integers this means both values lie in the inclusive range −3 through +3:

```c
if (-3 <= coarse && coarse <= 3 && -3 <= fine && fine <= 3)
    spectrum[k] = 0.0f;
else
    spectrum[k] = (float)((double)coarse * coarse_step
                       + (double)fine * fine_step);
```

The machine comparisons use unsigned arithmetic after adding 3; this pseudocode describes the decoded-value domain. The gate operates **before band scaling**, so small encoded integers need not correspond to inaudible output. Zeroing legitimate coefficient pairs changes the reconstructed spectrum.

This gate was absent from the public fixed-point and floating-point sources, available history and additional fork snapshots examined during the investigation. It is therefore described as an **additional downstream modification present in the v1.3 firmware**. Its original author and purpose remain unknown; it is not attributed personally to TempoTec.

## TEST 2: final isolated correction

TEST 2 kept the original v1.3 decoder and bypassed **only this gate**. The complete v1.2 decoder is no longer needed.

| Property | Value |
|---|---|
| File | `/usr/lib/libldacdec.so.1`, 28,804 bytes |
| Instruction offset / VA | `0x3b80` |
| Original instruction | `10 00 40 10` (conditional branch to `0x3bc4`) |
| Patched instruction | `10 00 00 10` (unconditional branch to existing weighted-sum path) |
| Actual byte delta | `0x3b82`: `40 → 00` |
| Delay slot | Multiply at `0x3b84` unchanged |
| Stock SHA-256 | `0427893de5def29975bc3bdf578fef32bc6e6300b73801d4813f0f918ceedb49` |
| Patched SHA-256 | `0f6e179f2e7fd31b5700cd0f0bbfaa4fca25b56201439c0c5b64eee96e14ca2d` |

**TEST 2 hardware testing confirmed that the isolated decoder condition was responsible for the audible v1.3 LDAC corruption.** Corruption disappeared completely on the physical V3 Blaze. TEST 2 booted, retained the stock interface, PEQ, real-time Bluetooth search and the official v1.3 stability improvement. Both editions use this exact decoder correction; it is independent of the theme and custom player patch.

## Origin investigation: confirmed findings and hypotheses

PEQ integration changes are in the player, and the relevant BlueALSA caller remains compatible. No demonstrated dependency links the gate to PEQ. A CPU optimization is a weak explanation: bitstream parsing and coefficient decoding have already occurred, both weighted multiplications execute even on the zero-output path, and scaling/IMDCT still follow.

Public LDAC history includes a fixed-point change concerning a “noise instead of silence” problem. The v1.2 binary contains behavior corresponding to the corrected fixed-point implementation. The floating-point variant in v1.3 differs, including handling of scale-factor index zero. A crude noise/silence workaround is **one hypothesis** for the downstream gate. It tests raw coefficients rather than scale-factor zero and cannot be equated to that public fix. Hardware testing establishes causality for corruption, not the author's motivation.

## Evidence boundary

Source records: local `v3-ldac-analysis/PHASE1-REPORT.md`, `decoder-investigation/DECODER-REGRESSION.md`, `decoder-investigation/DECODER-ORIGIN.md`, TEST 1/TEST 2 manifests, capture extraction and user-reported hardware PASS. Original research was reused rather than repeated. Portable [TEST 2 verification](evidence/stock-fix-FINAL-VERIFICATION.json) and [decoder verification](evidence/stock-fix-decoder-patch.json) accompany the [edition manifests](../build/v1.3/).

The reboot improvement belongs to the official v1.3 base. This patch does not claim to fix reboot behavior, Bluetooth range, receiver sensitivity or interference.
