# Isolated quantization and exact affine capture

This fixture links the owned `native_vorbis_numeric` component and minimal SDK
runtime. It measures and materializes original packed lookup1/2 metadata,
captures vector, scalar and floor0-entry affine values, and optionally calls
the affine denominator/gain APIs. Direct affine cases bypass parsing explicitly.
No vendor headers/archive, private ABI, decoder or production app is linked.

The coordinator uses core0; the worker uses core1 on ESP32 and core0 on C3.
Priority3/stack16384 and the isolated DIO40/4MB profile are test settings.
Production task affinities and configuration are not changed by this fixture.

Generate `cases.json`, `cases.h` and independent expectations with
`tests/test-vorbis-quantization.py`. Run `tests/run-vorbis-quantization-qemu.py`
with explicit hashes for both component C files, both public headers, component
CMake, JSON/header and QEMU, plus explicit ROM and pinned SDK/tool locations.
The controller reads back every literal packet byte, entry, affine field and
descriptor before configuration, then freezes component, fixture and data.
When present, `codebook.c`, `setup.c`, `floor_packet.c` and their headers are frozen and hashed as
build dependencies; this runner's checks still cover its quantization subset.

The 152 copied API controls exercise lookup0/reserved metadata, bounded and
maximum counts, truncation, capacity, invalid indices, vector/scalar/floor
semantics and unchanged outputs on failures. Scientific cases emit raw layouts,
materialized multiplicands and four uint32 fields per exact affine value.
Optional math captures status, kind, binary64 mantissa bits and signed exponent.
Guards surround outputs; packet, entry, book/layout, multiplicands and affine
math inputs remain unchanged. Composed gain equality is internal consistency,
not an independent numerical check. These finite controls are not a complete
Vorbis conformance suite.

`CHECKED_QUANTIZATION_CAPTURED` / exit0 confirms complete guarded capture only.
`passed` and `numerical_qualified` remain false; the separate Fraction/Decimal
checker compares exact fields and numerical values with its declared policy.
There is no synthesis, PCM, radio, real-time or physical qualification here.

The fixture alone adds `-fstack-usage` to both component compilation units.
Retained `.su` files are compiler per-function frame estimates, excluding
callee/libm stacks, task high-water measurements and physical performance.
