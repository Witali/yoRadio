# Exact S16 conversion of two independently scaled binary64 terms

The [API](../../../idf/components/native_vorbis_pcm/include/native_vorbis_pcm.h)
and [design](../../../docs/CYD_VORBIS_PCM_PAIR_DESIGN.md) compute nearest-even
of(a*2^Ea+b*2^Eb)*32768, then saturate to signed16. All finite binary64 values
and both full signed64 exponents are accepted. Exact integer/dyadic comparisons
preserve cancellation and arbitrarily tiny half-tie perturbations, without
materializing overflowing physical values or clipping individual terms.

Final host04, GCC13.3 ASan/UBSan with assertions enabled:

- 2,479 batches/478,388 exact PCM values,186 refusals/4,986,045 checks.
- All65,538 signed half-code boundaries around and beyond the PCM endpoints;
  positive/negative INT64_MIN infinitesimals, subnormal tie breakers, integer
  codes and saturation edges;2,047 finite binary64 exponent fields, significand
  widths1..53, exponent distances-2..2, extreme-scale matrix and huge cancellation.
- Independent Python integer sums/division, with2,033 Fraction/symbolic anchors.
  No tolerance: every output must equal the exact expected integer. Expected
  PCM SHA256:78142d17534b173c6a01c91b71a89bc7c5889eeaaf32f4edaddd0fbbf178de74.
- Immediate byte snapshots cover the supplied descriptors and actual input
  arrays, including injected NaN/Inf before restoration. Failed calls leave
  output unchanged; zero count permits null arrays/output, with descriptors
  still required. Source sharing is allowed; output is disjoint.
- Three supervised commands terminal0, outer CLI0, child processes reaped and
  groups gone; sanitizer stderr empty. Seven damaged captures are rejected.

Source-only GCC15.2 C/C++17 yields four ELF32 objects for LX6/RV32IMC; eight
commands terminate0. Production Clang-Tidy0warnings/0errors. Five fixture
warnings concern its own pre-call object-byte snapshots including padding;
no warning is suppressed. Public own frame176B on both ISA; private ternary
comparator336/320B excludes callees/task high-water. Runtime performance is
unqualified: the current exact boundary performs16 comparisons per sample.
No SDK/QEMU, firmware image, production selection or task/core/stack change.

Host01 stopped before GCC at WSL E_ACCESSDENIED; host02 compilation failed on
two -Wmisleading-indentation fixture lines. Formatting alone changed before
host03. Host04 adds pure corruption-reader checks; capture03/04 is byte-identical.
Profiles01 stopped before compiler execution with Windows DLL error623;
profiles02 passed. Packaging initially expected another report key; it was
corrected to the actual schema before creating the archive, without changing
any test data, comparison or capture. All host/profile attempts are retained.

`captures.zip`:235 members,50,736,066 uncompressed bytes;6,370,124 compressed.
SHA256:`d96b5cbe53cee88ca78d5f4fb4e43dd72b5fc8676f64b55d92c2d575d413e648`.
`manifest.json` SHA256:
`1cab066613634e0cd0240389c45c783c536df6e620e86d6cc4da83f4a6bbedd0`.
Frozen inputs/sources, captures, commands/receipts, diagnostics and source-profile
objects are retained. Rebuildable host executables/objects are omitted with
identities recorded. `replay.json` records packaging replay; `verification.json`
is independent root replay. The [pure verifier](../../verify-vorbis-pcm-pair-checkpoint.py)
checks every archived byte, full original inputs, all478,388 outputs, anchors,
command outcomes and corruption controls without extraction or archived execution.

Exactness applies only to the supplied terms. Earlier floor/IMDCT/window rounding
and underflow, arbitrary floor0 spans, granule/EOS, full31 PCM/bound2/all14 relations,
raw/radio integration, target performance and native/physical/deferred gates remain.
