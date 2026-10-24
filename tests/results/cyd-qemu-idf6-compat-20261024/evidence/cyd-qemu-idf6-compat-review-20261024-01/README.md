# Independent QEMU classic ESP32 / IDF6 source review

The proposed patch passes this source-only review with no blocking finding.
All 15 indexed members and 16 physical files match; 19 local primary source
pins and 36 frozen context pins remain exact. Five raw original copies are
exact, and an independent unified-diff parser reconstructs all six overlays.
The Python regression driver was AST-parsed, never imported or executed.

SDK6 explicitly uses QIO 28 address bits plus five quad clocks. Combined SSI
packing correctly emits six bytes after the opcode, rather than seven. DIO
28/2 emits four. The normal 24-bit fast/DOUT/QOUT/DIO/QIO forms preserve their
explicit byte contract and backing-data expectations. Dummy receive bytes do
not enter caller data. DPORT +0xcc is real full32-bit state with documented
reset0xfffce030 and ordinary RMW writes, rather than fabricated PHY success.

The driver has 187 planned independent comparisons. Root must retain exactly
187 actual rows with zero failures plus complete owned-process cleanup, real
EOF, reader join and unchanged inputs. Its60-second deadline covers the MMIO
phase, with bounded cleanup afterwards. Its32MiB bounds use polling and final
overshoot rejection, not a hard OS quota. No board, firmware, listener or guest
CPU execution is part of this fixture.

No test/build/QEMU/Git command or prepared function was run in this review.
Original production firmware and all prior NONPASS evidence remain unchanged.
The byte-oriented model does not establish arbitrary waveform accuracy, full
flash/hardware conformance, RF/calibration, production startup, physical audio,
network operation or performance. See review.json for exact scope and pins.

Primary hardware sources checked were the official Espressif ESP32 TRM and
GigaDevice GD25Q32C datasheet; exact URLs/access limits are recorded separately.
The official TRM currently returned version5.9, while the prep records an older
version5.7 fetch. The direct GigaDevice fetch timed out; official search text
and pinned local model/SDK sources provide the narrow readback described.
