# Actual packet-frame floor0 spectrum and reused IMDCT

The [component](../../../idf/components/native_vorbis_floor0_spectrum/README.md)
and [design](../../../docs/CYD_VORBIS_FLOOR0_SPECTRUM_DESIGN.md) preserve the
original exact residue/LSP/amplitude data, classify active floor domains and
prepare a scaled binary64 candidate. Integer residue multiplies the dyadic
gain factor before a single rounding. This is an unselected component and
host qualification, with no production task/configuration changes.

Final frame08, GCC 13.3 ASan/UBSan with assertions enabled:

- 447 raw packets/894 channels include all 434 original packets and 13 genuine
  packet supplements. Actual C header/setup/audio parsing precedes floor
  application and IMDCT; gains are not injected from an older capture.
- All original packet bytes, modes, cursors, header identities and fourteen
  relation identities are preserved. Original floor0 covers 168 packets/336
  channels, floor1 covers 532 channels through its unchanged exact path.
  Relation identities here do not mean newly qualified PCM relations.
- 116,960 joint-rounding values agree exactly with the integer oracle.
  For 5,376 nonzero original floor0 values, 800-digit independent gain references
  yield maximum relative error 4.850438525866904e-15 against the fixed 2e-12
  bound. All 751,360 IMDCT values satisfy the unchanged 5e-12 error/L1 bound;
  observed maximum 8.881784197001252e-16. The existing independent FFT oracle
  retains its 286 high-precision anchors and fixed 5e-13 anchor bound.
- Supplements cover absent floors with coupled nonzero residue, absent zero
  domains, order0, exact unity, poles, indeterminate0/0, poles with zero residue,
  active zero rate/map, finite-zero shortcuts, precision and wider routes.
  The final supplement explicitly verifies tiny-negative-log normalization:
  two near-unity amplitude63 channels produce the correct unity factor while
  retaining approximate provenance. It uses owned public packet arithmetic,
  not the deferred Xiph amplitude port.
- 4,522 expected refusals/5,155,393 guard checks, zero remaining allocations,
  ten corrupted captures rejected. All three owned commands and outer CLI
  completed with exit code 0; child reaping/group disappearance and empty sanitizer stderr
  are retained. There are 348 materialized floor0 channels and 14 explicit
  noncandidate domain/precision/wider channels; no fallback is claimed.

Final math03 independently checks 81,384 rows: 79,210 exact products,
2,851,560 product words, 66,151 rounded values, all 1,087 source widths,
53 nonzero factor widths and 1,661 working tops. It preserves 10,142 midpoint
ties, 13,518 carries, 2,174 invalid rows, 444 shape controls and 7,100,180 checks.
Nine corrupted captures are rejected. All owned commands/outer CLI exit with code 0,
ASan/UBSan stderr is empty. No decoder/gain/transform is run by this math test.

Source-only GCC 15.2 C/C++17 produces six ELF32 objects for LX6/RV32IMC across
ten successful commands. Both production C units have zero Clang warnings/errors.
Own function frames, with -O2/-fno-inline: prepare 400/384 B,
materialize 272/272 B, product 176/192 B and round 64 B, excluding callees and task
high-water. The integer fixture has zero Clang warnings/errors. Frame fixture
has twelve intentional diagnostics: one reused C-fixture include and eleven
pre-call byte-snapshot comparisons. No suppression or weakened assertion.

Every attempt remains preserved. Math01 and frame01 encounter sandbox WSL
E_ACCESSDENIED before GCC. Math02 completed C and comparisons but its corpus
invariant found two carry witnesses with incorrectly declared strict width54;
declaring their unchanged2^54 integers as width55 fixes the generator in
math03. Frame02 stops on misleading indentation in fixture formatting;
frame03 completes C but its Python Bark comparison incorrectly compares list
to tuple. Frame04 passes original 434 after comparison normalization. Frame05
stops before any command because an explicit independent setup reference was
not initialized. Frame06 passes434+12 supplements; frame07 strengthens guards
and corruption controls with the same case count; frame08 adds the required
thirteenth normalization regression. No production source or numeric bound
was changed to repair these fixture/controller errors. Flags in an early
failed report describe intended scope, not proof of execution.

The initial pure checkpoint reader passes all numerical comparisons and
nineteen corruption controls, then fails its stack-report text comparison:
the archived compiler files use CRLF while the profile JSON stores normalized
LF text. `replay-attempt01.json` preserves its actual traceback, verifier hash
and terminal exit code. The reader correction normalizes CRLF for this text
comparison only; raw member hashes and numerical bounds remain unchanged.
The complete corrected replay02 then passes with exit code0; its exact JSON
is retained in `replay.json` and independently sealed by root.

`captures.zip`: 731 members, 128,907,598 decoded bytes; 21,780,198 ZIP bytes.
SHA256:`c45e814f94f3462be4d4e5d054253d8d5fdbbec24e15d29b605da8eb4c2d9fb0`.
`manifest.json` SHA256:
`1b04de449a6361bb33511ae826628aacf3e832ce02854675344e5433f77f613b`.
Frozen sources, raw inputs/captures, diagnostics, process receipts and six
source-profile ELF objects are included. Seven rebuildable host executables
are omitted with byte counts and SHA256 recorded. The
[pure verifier](../../verify-vorbis-floor0-spectrum-checkpoint.py) uses pinned
live readers, checks every archived member and replays the independent models;
it executes no archived code, extracts no files and starts no child commands.
`replay.json` records the full pure replay; `verification.json` records root
verification of the exact archive, executed sources and replay artifacts.

This qualification executes no window, overlap, granule trimming, PCM,
SDK/QEMU or radio. The deferred overlap/PCM controller is untouched. Candidate
gain accuracy is established only for this finite corpus; general refinement,
complete wider fallback, known window underflow, original31 PCM/bound2/all14
PCM relations, public raw/audio-task integration and native/resource/physical
qualification remain open. Baseline Ogg/Vorbis playback continues to use the
existing Espressif decoder.
