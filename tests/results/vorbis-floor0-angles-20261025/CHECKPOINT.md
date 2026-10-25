# Original-angle floor0 arithmetic, 2026-10-25

The [numerical component](../../../idf/components/native_vorbis_numeric/README.md)
now evaluates the floor0 denominator and scaled log2 gain from original finite
binary64 LSP angles and mathematical `theta=pi*bin/map`. It implements
[Vorbis I 6.2.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html), with the
parity equations cross-checked against [Xiph v1.3.7 lsp.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/lsp.c).

The new `denominator_at_bin` / `gain_from_angles` APIs avoid rounding LSPs to
cosines. Cosine differences become products of half-angle sines; integer phase
reduction retains 1152 fractional bits with a 2304-bit `2/pi` constant. Small
sines remain scaled rather than underflowing during halving. Orders 1..255,
all finite binary64 angles, signs, subnormals, values outside `[0,pi]` and full
0..63-bit amplitude / 0..255 offset fields are accepted. There is no allocation,
variable-length array, arbitrary near-root pole test or change to vendor types.

## Actual verification

- The prior coefficient regression passes all 60541 operations under ASan/UBSan.
  Its complete binary output remains byte-identical:
  `475d0558e6cfbbb083bdf9a0f76b0da1dfdb0a985103c4a482dda87b2ec9e960`.
  Actual terminal `12faba` exits0.
- The new whole-module host campaign passes 2376 angle cases plus 28 metadata,
  output-preservation and invalid-input controls under ASan/UBSan. The independent
  oracle derives pi through directed Chudnovsky intervals and integer square
  roots, then directly evaluates cosine/P/Q at Decimal800..1184. It does not use
  the component's integer phase or sine-product algorithm. It separately verifies
  all 72 `2/pi` limbs. All four nonce-owned compiler/version/run commands finish
  normally with process-group cleanup. Actual terminal `618e14` exits0.
- Pure exact-rational Machin intervals and continued fractions independently
  certify the constant and the global nonzero phase gap. At least 77 significant
  phase bits remain, including the smallest subnormal. This certificate concerns
  phase reduction precision; it does not qualify libm or total floating error.
  Actual terminal `3e4bd9` exits0.
- Twelve pure literal/event tests pass. These test case identity, full-width raw
  values, malformed/missing/reordered/duplicated C data and native events, invalid
  normalization and guards. They do not execute or qualify numerical outputs.
  Actual terminal `981bf7` exits0.
- Each native whole-component SDK/QEMU capture finishes 200 cases, 212 events,
  eight API groups and nine commands with zero compiler warnings. ESP32 uses
  SDK6.0.2/Xtensa/machine94 and worker core1; C3 uses the pinned SDK6.1/RV32/
  machine243 and core0. Both coordinators remain core0; numerical workers use
  priority3/stack16384.
  Actual terminals `b87a22` and `661ed0` exit0. Capture reports deliberately keep
  numerical-qualified false until the separate comparison.
- The separate comparator replays every host input/output and all 2376 numerical
  comparisons, validates complete native C/readback/events, regenerates every
  expected value and accepts all 400 native values. Actual terminal `a0e355`
  exits0. Comparison report SHA256:
  `18994bb7b64f9e174f883dd8c2b55d3d67a5ebecb26255936aa9b0b75befc397`.

The engineering policy precedes component measurement: denominator relative
error <=`2e-12`; composed log2 gain absolute error
<=`2e-12 * max(1, abs(reference))`. Maximum observed denominator relative error
is `8.526e-14` on the host and `3.742e-14` on each native target. Full failed
and passing metrics remain in the reports. Relative gain error near zero can be
very large; a relative gain bound or exact sign through an approximate D is not
claimed. Extremely large scaled logarithms can also have large absolute errors
within the combined policy. The strict deficit-one/raw63 test for an exactly
supplied D=1 remains a separate unchanged coefficient/gain test.

## Scope and continuation

The module remains outside both production application component lists and
decoder registration. No physical board or production firmware is involved.
Production task cores/priorities/stacks, display and all three CYD audio
backends remain unchanged. Native compiler `.su` estimates have maximum own
frames of 800/784 bytes; these exclude callee/libm/task high-water and physical
throughput. The fixtures are emulator numerical tests, not firmware hand-offs.

Original owned setup/dequantization must still feed angles without Q24
narrowing. Wide residue/coupling, floor multiplication, IMDCT/overlap, final
PCM conversion and public raw lifetime/retry/reset/integration still require
implementation and qualification. The historical full31 PCM NONPASS remains
open. This checkpoint does not close full floor0/G6/G8, resume deferred scopes
or establish physical real-time behavior. See the
[wide synthesis design](../../../docs/VORBIS_WIDE_NUMERIC_DESIGN.md).

The archive's offline replay reuses explicitly pinned pure oracle/protocol
definitions and recomputes the new host/native numbers and phase certificate.
It checks integrity and byte parity of the old coefficient regression without
recomputing its earlier mathematical campaign. Omitted executables/full ELF/
flash images have identity only. ELF52 headers prove architecture, not complete
binary semantics; selected SDK metadata does not provide full dependency closure.
