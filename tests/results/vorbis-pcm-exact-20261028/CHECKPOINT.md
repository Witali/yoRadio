# Complete exact-window products through final S16 rounding

The [API](../../../idf/components/native_vorbis_pcm_exact/include/native_vorbis_pcm_exact.h)
and [design](../../../docs/CYD_VORBIS_EXACT_PCM_DESIGN.md) add both complete
106-bit dyadic products before nearest-even rounding and signed16 saturation.
The lazy-window adapter reads actual-neighbor slices without materialized
product arrays. Base exponents stay symbolic; no intermediate double product,
sum, scale or per-term clipping can discard cancellation or a half-tie tail.

Final host05, GCC 13.3 ASan/UBSan with assertions enabled:

- Every original 2,479 PCM batch / 478,388 output is retained. Captured old
  source bits, scale fields and final S16 bytes are preserved byte-for-byte;
  samples enter the new route via exact multiplication by unity. The old
  PCM C implementation is not compiled or called. Its pinned live pure reader
  and committed captures are used only for independent data/reference checks.
- 208,411 new scalar rows include all 65,538 half boundaries with three tiny
  perturbation signs, widths 1..106, all selected shift/base endpoints,
  malformed products/nulls and four genuine multiply-to-PCM handoffs. In
  particular, `(1+2^-52)*(1-2^-53)` at base -16 rounds to +1 (or -1 with sign),
  and its near-cancellation at base38 retains one code; narrowing the product
  first loses these tails. The final 432-row width64/65/105/106 matrix directly
  covers same-sign low-word carry and up-to108-bit merge at distances0/1/2.
- All 864 saved overlap DATA rows / 648 ready rows produce 598,992 exact new
  adapter outputs. Every one of their 1,197,984 complete window terms agrees
  with integer-ratio multiplication. All 17,962 former underflow identities,
  including 13,767 with base >=1074, remain present/nonzero before final sum.
  The older overlap C API and deferred composition controller are not run.
- Actual previous/current full unwindowed sources, scales, prepared coefficients
  and record identities are reconstructed from pinned data. Slices use A/2
  and `((int32_t)B-(int32_t)A)/4`, preserving negative long-to-short origins.
  Priming records emit nothing and use a valid dummy previous view for count0.
  No synthetic terminal packet or new history/reset policy is introduced.
- All 8,160 coefficients preserve the existing 70-digit sine reference bound
  2e-15. Python arbitrary-precision integer sums and exact division/remainder
  define the new oracle; huge gaps preserve the sign of an infinitesimal only
  at an exact half tie. Both the old and new independent Fraction/symbolic
  anchor sets pass 2,033 checks each.
- 4,178 expected refusals / 62,379,152 guard checks; 14 damaged captures are
  rejected. Failure snapshots preserve actual source/view/output bytes, even
  for selected late NaN/Inf before restoration. All three owned commands and
  outer controller exit0, children are reaped/groups gone, ASan/UBSan stderr
  is empty. Alternate floating rounding modes do not affect integer conversion.

Source-only GCC 15.2 C/C++17 passes ten commands and produces six ELF32 objects
for LX6/RV32IMC. Both production C units have zero Clang warnings/errors.
Own frames at -O2/-fno-inline: public scalar192/192 B, slice adapter112/112 B,
private three_sign320/304 B and rounded_sample256/288 B. These exclude callees
and task high-water. Fixture lint02 has 27 displayed / 48 generated warnings,
five default system-header suppressions and zero errors: one reused C-fixture
include and 26 deliberate pre-call byte-snapshot comparisons are displayed.
No custom suppression or altered lint configuration is introduced.

All attempts survive. Host01 stops before commands because the frozen pure
window reader derives ROOT from its new snapshot path; the controller then
reads pinned data through its explicit repository ROOT. Host02 records sandbox
WSL refusal before GCC. Host03 completes C and every numerical comparison,
then finds a corruption probe that writes zero over an already-zero output.
Host04 passes after that probe flips one bit and every mutation is required
to change the body. Host03/04 numerical captures and inputs are byte-identical.
The final host05 adds the bounded wide-carry matrix and an explicit fixture
allocator cap, resolving lint01's tainted-allocation warning. No production
source, prior datum, numerical reference or bound changes during these repairs.
Only the owned-process supervisor timeout cap is derived from60 to180 seconds;
nonce/request binding, group termination/reaping and the original controller
remain unchanged. No SDK/production watchdog or idle-task setting is changed.

`captures.zip` SHA256:
`e47fe7e135c1c78af04250b0cc92d78b3619aecf530cced6801af9723d1f2b97`.
ZIP bytes:37,630,511. `manifest.json` SHA256:
`8719e3aaed4851420a941331ac6b2032d8e345cfa85654d7dd9feffc4c29ba16`.
The manifest preserves all 431 logical files / 611,118,904 logical bytes.
Identical member bytes share 124 physical SHA256 blobs / 302,750,255 decoded
bytes; no logical input/source/capture/case is removed. Every mapping, byte
count, hash, canonical path and complete blob usage is checked. This avoids
publishing repeated copies of identical data while retaining every attempt.
Three rebuildable host executables are omitted with identities recorded;
source-profile ELF objects remain. The
[pure verifier](../../verify-vorbis-pcm-exact-checkpoint.py) uses pinned live
readers, starts no commands and executes/extracts no archived code. `replay.json`
records its complete numerical replay; `verification.json` records separate
root artifact/replay verification without repeating that numerical campaign.

This qualifies the new exact-window-to-S16 boundary for supplied dyadics.
It does not qualify preceding floor/IMDCT approximation, arbitrary wider
gain/transform routes, a production history owner, granule trimming/raw/radio,
original31 full decoder PCM/bound2/all14 relations, native/resources/real-time
performance or physical acceptance. The existing APIs, production selection,
task cores/stacks/priorities/backends and old deferred records are unchanged.
