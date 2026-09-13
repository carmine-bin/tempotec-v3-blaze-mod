# Bluetooth range/interference

**UNRESOLVED / UNDER INVESTIGATION** — neither edition claims to fix Bluetooth range.

Hardware observations on this V3 Blaze show that higher-bandwidth Bluetooth codecs / LDAC modes are unreliable. Higher LDAC rates can produce repeated playback dropouts. Lower-rate LDAC can also have noticeable cuts in difficult real-world environments, especially around many people and wireless devices. Under the same normal-use conditions, AAC works effectively perfectly and is dramatically more reliable.

The remaining symptom is strongly related to link margin/interference. This is a separate issue from the [v1.3 decoder corruption](LDAC-REGRESSION.md), which was audible even with continuous RTP reception and is corrected by TEST 2. These observations are specific to the tested device and scenarios, not universal claims about codecs.

Wi-Fi range also appears unusually poor under similar physical conditions. The Broadcom combo platform handles Wi-Fi and Bluetooth; they may share part of the RF path/configuration. This is relevant investigative context, **not an established cause**.

Possible areas under investigation, all hypotheses:

- Antenna or antenna contact; RF matching; shared Wi-Fi/Bluetooth RF path.
- Receiver sensitivity; Broadcom RF/NVRAM configuration; Wi-Fi/Bluetooth coexistence.
- Bluetooth link management; hardware degradation; another firmware/configuration problem.

The underlying cause remains unknown. AAC is the reliable fallback in the observed normal-use scenarios. Evidence: user-reported hardware observations, supplied for this repository update; no new RF experiment was performed.
