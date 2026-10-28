# Reused Xiph IMDCT: normalized binary64 entry

Scope: a new representation entry into the existing unchanged inverse-transform
kernel. No floor0 gain, window/overlap, PCM, SDK/QEMU or radio is executed here.
The old limb entry and generated Xiph bodies are unchanged. Production lists,
task affinity, priorities/stacks, displays and audio backends are unchanged.

The [API](../../../idf/components/native_vorbis_transform/include/native_vorbis_transform.h)
and [design](../../../docs/CYD_VORBIS_NORMALIZED_IMDCT_DESIGN.md) specify finite
inputs bounded by2^639, borrowed storage and an unchanged signed64 exponent.
`RANGE` means the internal representation needs normalization or a wider route;
it does not authorize rejecting a valid Vorbis stream.

- Final host04: 1,729 rows, 1,280,448 time values, all eight block sizes.
- 301,248 values are compared bit-for-bit with the old limb route inside the
  assert-enabled C fixture. All1..1151 widths and selected endpoints are covered.
- 336 refusals, 5,589,927 assertions; source bytes, supplied descriptors,
  output/result, lookup/prefix/tails and retry are checked. Each refusal checks
  injected nonfinite bytes before the fixture restores them.
- Seven supervised commands terminate0 with child reaped/process group gone;
  outer CLI terminates0. GCC13.3 ASan/UBSan reports no diagnostics.
- Independent complex-FFT comparison retains286 Decimal/rational anchors.
  Fixed bound:5e-12*L1(input)+32*N*DBL_TRUE_MIN.
- Maximum normal-input error/L1:2.6506574712925612e-15. The separately reported
  subnormal maximum0.49994464825754625 is covered by the absolute underflow term,
  and is not an ordinary relative-precision claim.
- Source GCC15.2:12 terminal0 commands, six ELF32 C/C++ objects across LX6 and
  RV32IMC. New entry own frames128/144B exclude callees/task high-water.
- Clang-Tidy: conversion/transform0warnings/0errors. Final fixture has three
  warnings for its own pre-call byte snapshots; padding preservation is an
  intentional assertion, rather than equality of independently built objects.
  No suppression is added.

History is preserved. Host01 stopped before GCC at sandbox WSL E_ACCESSDENIED.
Host02 passed; host03 separated normal/subnormal metrics; host04 strengthened
per-refusal snapshots. Final capture is byte-identical to host03. GCC01 failed
before compiler execution with Windows DLL error623; GCC02 passed. A first root
checkpoint replay expected a nonexistent `passed` field in the GCC report;
its reader now checks the actual completed/12-command/terminal0 schema, without
changing any captured artifact or numerical expectation.

`captures.zip`:320 members,47,673,094 uncompressed bytes;12,902,397 compressed.
SHA256:`92ef522d3707836307333694257fa2f4330e6edb32be1b3041f3e5112f9af1f4`.
`manifest.json` SHA256:
`a6b528502ec1dc86546e2596631883f57497d3ed8b3efe9a69014e64d244f305`.
Sources, compiler/profile objects, commands/receipts, diagnostics, previous
attempts and every numerical capture are retained. Rebuildable host executables
and host object directories are omitted; their recorded identities remain.

The [pure verifier](../../verify-vorbis-normalized-transform-checkpoint.py)
checks every archived byte, complete capture, all anchors, command outcomes,
instrumentation and source profiles. Five damaged captures must be rejected.
It uses pinned local readers, extracts nothing and runs no archived code or
child command. `verification.json` is the independently replayed result;
`replay.json` records the packaging-time replay. Deferred scopes remain open.
