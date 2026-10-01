# Rejected implicit-SBR flag experiment

The native decoder disables AAC-Plus after an initial LC frame. Identical ADTS
core headers do not signal the later arrival of implicit SBR/PS to the adapter.
The existing full-format tests therefore require a restart for that transition.

The first source-wrapper experiment restored `external[7] = 1` and core byte 8
before every `PVMP4AudioDecodeFrame` call. It changed no DSP or allocations.
The first eight format cases completed in QEMU, but LC 22.05 kHz mono followed
by implicit HE-AAC v2 caused a **load access fault**, not a successful transition.
The retained RV32 disassembly places the fault inside `PVMP4AudioDecodeFrame`:
it loads a null pointer from core offset 0x2c, then reads pointer + 0x348.
This observation does not identify the first corrupting write.

**Rejected; never flashed to the board.** The wrapper and build option were
removed from active sources. A flag-only change is not an acceptable repair.
The decompiled controller additionally gates `sbr_open` on the overall frame
counter being less than two. Investigate late owner/control initialization,
PCM output lengths and rate/channel publication before another candidate.
Do not reset AAC transform history simply to force that frame-counter branch.

[Retained experiment](../tests/results/esp32c3-aac-continuity-rejected-20261001/)
contains the source wrapper, defaults, integration patch against `c9097402`,
exact config, ELF hash and raw QEMU fault log. It contains no successful PCM
quality claim. To reproduce, apply the patch in an isolated checkout at that
commit and copy the two source/default files back to their named locations;
use only a disposable QEMU flash image, never physical application OTA.
