# Credits

TempoTec supplies the V3 Blaze, official `V3_ANALOG_2025` firmware and stock assets. HiBy supplies the interface design, player, litegui engine and layout format. Proprietary component authorship is not inferred from firmware distribution.

Kae0 adapted the HiBy R3 Pro II 2025 design to the V3 Analog at losber's request. Full Mod adapts that port to the Blaze and corrects its device-specific layouts and controls. [Original Head-Fi post](https://www.head-fi.org/threads/hiby-r3-ii-new-and-improved-physical-volume-knob-4-4mm-balanced-out-increased-power.969585/page-15#post-18600653), March 4, 2025. losber requested the Analog version and supplied its stock firmware.

Historical v1.2 documentation attributed 385 assets to Kae0's build, 187 to TempoTec stock and 109 to modifications made here. Those were reported provenance figures, not verified current counts; a later audit counted 675 PNGs in the shipped v1.2 theme. The current [Full Mod manifest](build/v1.3/full-mod-manifest.json) records firmware differences, not artwork authorship.

Community research and tools:

- [hiby-modding/hiby_os_crack](https://github.com/hiby-modding/hiby_os_crack): repacking, HiBy recovery research and X1600E material.
- [Ingenic-community/Cloner](https://github.com/Ingenic-community/Cloner): USB boot/recovery tooling. Full NAND recovery has not been exercised on this Blaze.
- [bidhata/Hiby-R1-Mod](https://github.com/bidhata/Hiby-R1-Mod): performance-setting ideas adapted where supported; the R1 and Blaze have different DACs and configuration flags.
- squashfs-tools, xorriso, libarchive, binutils, LLVM, QEMU MIPS, Ghidra, Pillow, adb, Python and historical fakeroot tooling.

The maintainer performed the receiver captures, decoder-isolation experiments and physical firmware/UI testing. Public decoder sources and pinned revisions are credited in the [decoder investigation](docs/evidence/DECODER-ORIGIN.md). The downstream coefficient gate's author and purpose are unknown.

Development and reverse-engineering work was assisted by AI tools. All released firmware changes were reviewed and tested on physical V3 Blaze hardware.

El desarrollo y parte del trabajo de ingeniería inversa contó con asistencia de herramientas de IA. Los cambios publicados del firmware fueron revisados y probados en hardware V3 Blaze real.

For attribution corrections, open an issue. Rights and licence scope are described in [NOTICE.md](NOTICE.md).
