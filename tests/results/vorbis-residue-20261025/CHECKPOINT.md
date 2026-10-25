# Owned exact Vorbis residue and coupling: 2026-10-25

The [three public APIs](../../../idf/components/native_vorbis_numeric/include/native_vorbis_residue.h)
and [implementation](../../../idf/components/native_vorbis_numeric/residue.c)
decode every submap of a selected mapping and apply inverse coupling. The
[design](../../../docs/VORBIS_RESIDUE_DESIGN.md) cites the public specification
and explains deliberate differences from Xiph's reference shortcuts.

All 10,980 host rows and 37 guarded API controls pass strict GCC and ASan/UBSan.
The corpus contains 306 originals and 10,674 explicit payload bit cuts.
There are 10,686 EOP-stop outcomes: the cuts plus 12 attempted reads with
pre-existing sticky EOP. Another six sticky-EOP cases require no read and do
not report a new stop. Expected INVALID cases preserve cursor/output/state;
classification scratch is explicitly working memory after decoding starts.

An independent Fraction oracle compares 7,143,388 uint32 limbs before and after
coupling exactly. Captures contain 223,899 classwords, 316,473 VQ words and
686,172 scalar contributions. Cases include all three scatter formats,
unaligned type2, eight passes, empty books, zero-width numeric storage with
mandatory entropy, oversized classword quotients, partial residue0 publication,
all coupling sign branches, and 34-limb cancellation/sign witnesses.
A host-only case decodes one complete sequenced 65,535-component VQ word;
this is the standalone bins-independent API, not a mode-matched audio frame.
Its 139,264 limbs are explicitly excluded from the native resource selection.
The earlier complete 24-bit sparse-entry parser qualification is not rerun here.

Each native SDK/QEMU capture completes 200 preselected originals, 37 controls,
1,353 events and nine normal commands with zero build warnings. ESP32 SDK 6.0.2
uses worker core1; C3 SDK 6.1.0 uses core0. Coordinator0, priority3/stack16384
are unchanged test settings. Separate exact replay accepts all 400 native
cases: 57,120 limb values, 2,866 classwords, 6,112 VQ words and 8,968 scalar
contributions. Native includes a smaller case with phrase dimension 65,535,
plus cases with 34 limbs, 255 channels and 256 coupling pairs.

Cross-target Clang-Tidy checks all six C units. Residue and the other newer
units have zero warnings; the previously triaged bounded-int floor0 warning
remains once per architecture. All seven current protocol suites pass.
Compiler own frames for measure/packet/coupling are 384/496/800 bytes on ESP32
and 368/496/768 on C3. These exclude callees, task high-water and real-time
performance; common-grid workspace depends on the encoded books and capacity.

The archive retains original inputs, exact outputs, source snapshots, command
receipts, diagnostics and isolated QEMU build files, rather than SDK installations.
Replay without a compiler, QEMU or source checkout dependencies:

```powershell
python -B -X utf8 tests/results/vorbis-residue-20261025/verify.py
```

[Fresh-run instructions](../../target/vorbis_residue_qemu/README.md) describe the
host and target commands. These are test images, not production radio firmware.
Floor multiplication, IMDCT/overlap, PCM conversion, frame/raw lifecycle and
production integration remain required. Historical full31 PCM NONPASS/G6/G8,
active zero-floor0 domains, explicitly deferred work and physical acceptance
remain open; production audio/display settings and task affinities are unchanged.
