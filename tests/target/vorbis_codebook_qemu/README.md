# Isolated codebook and Huffman capture

This fixture links the owned `native_vorbis_numeric` component and minimal SDK
runtime. It parses original codebook packets, materializes caller-owned Huffman
and quantization state, decodes LSB-first codewords, and captures exact affine
VQ/floor0 values. No vendor headers/archive, private ABI, stream decoder or
production application is linked.

The coordinator uses core0; the worker uses core1 on ESP32 and core0 on C3.
Priority3/stack16384 and the isolated DIO40/4MB profile are test settings.
Production task affinities and configuration are unchanged by this fixture.

Generate the bounded JSON/header corpus with the independent codebook oracle.
Run `tests/run-vorbis-codebook-qemu.py` with explicit hashes for all three
component C files, all three public headers, component CMake, JSON/header and
QEMU, plus explicit ROM and pinned SDK/tool locations. The controller reads
back every literal input byte and descriptor before SDK configuration, then
freezes the complete component, fixture and original data.

Guards surround caller-owned state and outputs; input packets, setup metadata
and materialized book state are checked for preservation. The 719 copied API controls
exercise malformed/truncated trees, capacity, indices, cursor EOP and unchanged
outputs on failure. The singleton erratum requires length1 and consumes one bit,
accepting either0 or1. These finite controls do not establish complete Vorbis
conformance.

Per-row setup and payload truncation counters are explicitly zero here. The
host campaign tests every preceding bit cutoff; native fixed controls exercise
representative transactional truncation and sticky-EOP failures separately.

`CHECKED_CODEBOOK_CAPTURED` / exit0 confirms complete guarded capture only.
`passed` and `numerical_qualified` remain false. A separate independent checker
must compare every exact codebook/Huffman/affine output against its own model.
There is no synthesis, PCM, radio, real-time or physical qualification here.

The fixture alone adds `-fstack-usage` to all three component compilation units.
Retained `.su` files are compiler per-function frame estimates, excluding
callee/libm stacks, task high-water measurements and physical performance.
