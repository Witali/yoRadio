# Isolated floor0 numerical capture

This test links only the owned `native_vorbis_numeric` arithmetic component and
the minimum SDK runtime. It uses no codec vendor headers, archive, private ABI,
stream decoder or production application. ESP32 uses a core0 coordinator and
core1 worker; C3 uses core0 for both. The worker has priority3/stack16384.

Generate the bounded JSON/header corpus using the independent host oracle,
then invoke `tests/run-vorbis-floor0-numeric-qemu.py` with explicit source,
public-header, component-CMake, JSON/header and QEMU hashes and an explicit ROM
directory. The controller freezes all three pinned component files and this
fixture before SDK configuration. When present, `quant.c`, `codebook.c`,
`setup.c` and their public headers are frozen and hashed as build dependencies.
This runner's API/numerical checks still cover its floor0 subset only.
Production components/configuration are not edited.

Each curve row captures the scaled denominator and logarithmic gain as exact
IEEE binary64 mantissa bits plus signed32 exponents and the returned kind.
Direct-gain rows mark denominator status `-99` (not called) and echo their input
denominator. Buffer guards, complete coefficient/amplitude input preservation,
denominator input preservation and normalized output shape are checked.
Separate finite API groups exercise all seven public functions, in-place
preparation, invalid calls, absent/pole/indeterminate/unity outcomes, Bark bounds
and exact cardinal cosine cases. These are not full API/conformance coverage.

`CHECKED_MATH_CAPTURED` / exit0 means the capture and structural checks completed.
It does not claim numerical success. Compare every returned value separately
against the original independent Decimal results and predeclared error policy.
No PCM, complete floor0 implementation, synthesis, real-time or physical-device
qualification follows from a passing arithmetic subset.

The fixture adds `-fstack-usage` only to its frozen numerical component and
retains the compiler `.su` file. These per-function frame estimates exclude
callee/libm stacks, task high-water measurements and physical performance.
