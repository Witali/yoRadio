# Exact quantization/VQ/LSP preservation, 2026-10-25

The [owned component](../../../idf/components/native_vorbis_numeric/README.md)
now parses the quantization section after the codeword lengths and reconstructs
lazy vector/scalar/floor0 LSP values through its
[public API](../../../idf/components/native_vorbis_numeric/include/native_vorbis_quant.h).
Original packed minimum/delta words and integer weights remain exact; a value
is `unpack(minimum)*A + unpack(delta)*B`. The affine floor API reduces these
individually exact terms separately, before a floating sum can lose information.

The [design](../../../docs/VORBIS_QUANTIZATION_DESIGN.md) follows
[Vorbis I 3.2/6.2.2/9.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
[Xiph sharedbook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c)
for lookup/sequence recurrence and the actual
[floor0 carry loop](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor0.c).
It preserves full declared lookup rows, not just sparse-used rows. It does not
inherit the reference library's packed-float exponent clamp. Prefix truncation
and the separate cross-vector carry match the reference loop.

## Actual verification

- Whole-component GCC/ASan/UBSan passes6572 cases and152 API/error/preservation
  controls. Independent exact Fraction computations check79834 exact values:
  77573 reconstructed from packets/entries and2261 direct affine inputs retained
  through floor calls, plus complete layout/packet fields and multiplicands.
  A separate1440-digit direct cosine/P/Q oracle accepts92 affine floor results.
  Both component C files and both public headers are frozen and compiled under
  strict warnings/floating flags. All four nonce-owned compiler/version/run
  commands finish with normal process/session cleanup. Actual terminal
  `351d79` exits0.
- Both native whole-component SDK/QEMU captures finish200 cases,1061 events,
  the same152 API controls and all nine commands with zero compiler warnings.
  The copied control function is byte-identical to the actual host adapter.
  ESP32 uses SDK6.0.2/Xtensa/machine94/core1; C3 uses pinnedSDK6.1/RV32/
  machine243/core0. Both coordinators remain core0; workers use priority3 and
  stack16384. Actual terminals `814f6c` and `0e4c18` exit0. Capture reports retain
  numerical-qualified false until independent comparison.
- The separate checker replays the complete6572 host input/output/model and
  every target event/value/source identity. All400 native cases,15036 exact
  affine values (10514 reconstructed and4522 direct inputs) and184 floor
  comparisons pass the unchanged policy. Actual
  terminal `932d56` exits0. Comparison report SHA256:
  `3c1db8263183b5e838f3f1135d070877444e591f5be1ccdb924419c22a5bba39`.
- The4096-bit `2/pi` constant and2304-bit fractional phase grid pass separate
  exact-rational Machin/continued-fraction certification. The affine nonzero
  phase gap exponent1904 leaves400 significant grid bits. This is a constant/
  phase proof, not a libm or total floating-error proof. Actual terminal
  `57675b` exits0. Independent Chudnovsky intervals also verify all128 limbs.
- Earlier coefficient60541 and angle2376 host regressions pass under sanitizers.
  Their entire output streams remain byte-identical to the preceding accepted
  runs (`475d0558...e960` and `3e669d33...fb42`). Actual terminals `350641` and
  `f7c770` exit0. Old archive bodies are unchanged. The canonical angle oracle's
  sole adaptation is selecting the current table size/precision.
- Twelve new pure literal/event tests pass (`7e85d3`). The two legacy controllers
  now freeze optional quantization dependencies before building the enlarged
  component; their original CLI/protocol and numerical scope are unchanged.
  Existing12/13 protocol suites pass (`81900a`/`fc9bb2`). Those pure tests do not
  execute a component or qualify a new legacy SDK run.

Exact symbolic fields are compared without tolerance. Floor denominator relative
error is bounded by2e-12; composed log2 gain uses absolute error
`2e-12 * max(1,abs(reference))`, declared before measurement. Maximum observed D
relative error is3.098e-14 on the host and each native target. Full metrics retain
large absolute log errors at extreme scale and relative errors near zero; no
universal absolute or relative gain-error bound is substituted for that policy.

## Ownership, resources and scope

Measure/materialize retains uint64 counts and bit spans; the maximum lookup2
count is1099494785025, irrespective of target size_t. Required caller capacity
and malformed/truncated metadata are distinguished. Validation precedes writes,
including late invalid entries/weights. Lazy scalar evaluates component65534 of
dimension65535 without allocating a complete output row. No allocation, VLA or
mutable global state is introduced in the component. Inputs/outputs obey the
documented immutable/disjoint ownership contract.

Native compiler own frames are floor1104/1072 and quant144/128 bytes. These
exclude callee/libm/task high-water and physical throughput. The test images
are isolated emulator fixtures, not production firmware hand-offs. Production
stream core0/decode-output core1, priorities/stacks, display and all three CYD
audio outputs are unchanged; the component remains outside radio registration.

Full entropy/Huffman/setup/audio packet parsing, wide residue/coupling, floor
multiplication, IMDCT/overlap, final PCM and public raw lifecycle/integration
remain required. Historical full31 PCM NONPASS, full floor0/G6/G8 and physical
acceptance remain open. No deferred public-consumer guard, Ogg or AAC work is
resumed by this independent data/numerical layer.

Offline replay reuses explicitly pinned pure Fraction/Decimal/protocol
definitions and recomputes every new host/native comparison and the phase
certificate, without a saved main/compiler/SDK/QEMU/decoder. The earlier two
regressions are checked for integrity and output byte parity offline, not by
rerunning their old mathematical campaigns. Omitted executables/full ELF/flash
have identity only; ELF52 proves architecture, not binary semantics, and
selected SDK metadata does not establish complete dependency closure.
