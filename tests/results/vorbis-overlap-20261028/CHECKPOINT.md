# Stateful Vorbis overlap, independent retained scales

The [API](../../../idf/components/native_vorbis_overlap/include/native_vorbis_overlap.h)
and [design](../../../docs/CYD_VORBIS_OVERLAP_DESIGN.md) use actual adjacent block
sizes and the Xiph reference geometry. The first block primes, later blocks
emit(A+B)/4 term pairs, reset discards history logically, and each accepted
block retains its unwindowed right half. No invented final zero block is used.

Final host03 passes GCC13.3 ASan/UBSan with assertions enabled:

- All36 legal size configurations, three patterns/eight-block sequences:
  864 blocks,648 emitting/216 priming,108 resets and all four transitions.
- Independent full-window/scatter oracle:1,197,984 contribution values and
  757,344 exact history values;185,904 exact plateau and185,904 support values.
- 57,376 exact opposite contribution pairs,144 silent-current rows preserving
  the preceding tail; signed64 exponent endpoints, signed zeros, DBL_MAX,
  normal minima and minimum subnormals are retained.
- 8,308 refusal controls/11,895,678 assertions. Every rejection snapshots and
  checks the actual input/history/output/state/descriptors before injected
  nonfinite bytes are restored. Capacity retry, unused tails and immutable
  plans/lookups are guarded in empty and active states.
- Three supervised commands terminal0, outer CLI0; child processes reaped and
  groups gone, sanitizer stderr empty. Ten damaged captures must be rejected.

Binary64 window multiplication has a known range limitation:17,962 nonzero
positive-slope operands round to zero, including13,767 with retained exponent
at least1074. Downstream exact addition cannot recover these lost terms. The
fixed error allowance remains2e-15*abs(operand)+4*DBL_TRUE_MIN, and the measured
maximum for normal operands is4.1390838976316517e-16. No input row is dropped or
tolerance widened. **Full-range synthesis/PCM is unqualified**, requiring wider
representation/routing; this record does not authorize rejecting valid formats.

Source-only GCC15.2 C/C++17 yields four ELF32 objects for LX6/RV32IMC; seven
commands terminate0. Push own frame128B on both ISA excludes callees/task
high-water. Clang-Tidy overlap0warnings/0errors. The fixture has19 warnings for
comparing its own pre-call object bytes, deliberately including padding; no
suppression is introduced. No SDK, QEMU, production image, task/core/stack change
or physical resource/performance claim is made.

Host01 stopped before GCC at sandbox WSL E_ACCESSDENIED. Host02 reached
compilation and failed -Wmisleading-indentation in two fixture if statements;
formatting alone changed before host03. All attempts/sources/diagnostics remain.
Production component, corpus and tolerances were unchanged by that repair.

`captures.zip`:228 members,29,134,003 uncompressed bytes;6,142,916 compressed.
SHA256:`685778be3a8650fd9e1740e2e99b1540b1f2cde7ec33046f96d3e3bde6fd2d23`.
`manifest.json` SHA256:
`cba1bd703fb6467828b56db3becd796eaf270f4ecdebf78025f5d3b577c54700`.
Frozen sources, captures, receipts, compiler/lint diagnostics and source-profile
objects are retained. Rebuildable host executables/host objects are omitted,
with executed identities recorded. `replay.json` is packaging-time replay;
`verification.json` is independent root replay. The
[pure verifier](../../verify-vorbis-overlap-checkpoint.py) checks every byte,
all measurements and ten corruption controls using pinned local readers,
without extraction, archived code execution or child commands.

Granule/EOS, floor0/wider synthesis, final PCM, original31/bound2/all14 relations,
raw/radio integration and native/physical/deferred gates remain open.
