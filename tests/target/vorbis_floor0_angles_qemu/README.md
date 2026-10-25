# Isolated original-angle floor0 capture

This test links the owned `native_vorbis_numeric` component and the minimum SDK
runtime. It calls `denominator_at_bin` and `gain_from_angles` with original
binary64 angles and mathematical `pi*bin/map_size`; it does not first round
angles or the bin to cosine coefficients. All finite angle values are accepted,
including negatives, signed zero, subnormals and values outside `[0,pi]`.
No vendor headers/archive, private ABI, decoder or production app is linked.

The fixture uses core0 for its coordinator and core1 for the ESP32 worker;
the C3 worker also uses core0. Priority3/stack16384 and the isolated DIO40/4MB
test profile preserve the previous test convention, not production settings.

Generate `cases.json`/`cases.h` and the independent expectations with the new
angle host oracle. Run `tests/run-vorbis-floor0-angles-qemu.py` with explicit
source, public-header, component-CMake, JSON/header and QEMU hashes plus the
explicit ROM directory. The controller reads back every descriptor and angle
bit before SDK configuration, then freezes the complete component/fixture.
When present, `quant.c`, `codebook.c`, `setup.c`, `floor_packet.c` and their headers are frozen as build
dependencies; this runner's checks still cover its original-angle subset only.

Every scientific case captures denominator/gain status, normalized binary64
mantissa bits, signed32 exponent and gain kind. Guards surround inputs and all
outputs, and the entire angle workspace, amplitude and denominator input remain
unchanged. Composed `gain_from_denominator(D)` equality is an internal consistency
check only; separate high-precision comparison supplies the numerical gate.

Eight finite API groups cover valid calls, composition, a tiny angle whose old
rounded cosine loses the positive denominator, full finite inputs, invalid
arguments with unchanged output, absent/pole/indeterminate outcomes and zero
offset unity. Raw zero follows the documented API contract: valid amplitude,
order and bin metadata are required, while the angle pointer is not read.
These groups do not establish complete API or Vorbis conformance.

`CHECKED_ANGLES_CAPTURED` / exit0 confirms complete guarded capture only.
`passed` and `numerical_qualified` stay false until a separate comparison against
the original independent expectation corpus and its predeclared policy.
No synthesis, PCM, radio, real-time or physical qualification is claimed.

The test alone adds `-fstack-usage` to the frozen component and retains `.su`
compiler frame estimates. These exclude callee/libm stacks, task high-water
measurements and physical performance. Production code/configuration and the
previous numeric fixtures/archives remain unchanged by this new test project.
