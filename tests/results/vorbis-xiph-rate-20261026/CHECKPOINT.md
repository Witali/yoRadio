# Unsigned Xiph identification rate checkpoint

Source commit: `3600c1ee5` (`fix: preserve unsigned Vorbis sample rates on 32-bit targets`).
[Design and consumer contract](../../../docs/CYD_XIPH_RATE_DESIGN.md).
The candidate remains outside both production radio component lists. No
production firmware is handed off and no physical board is used here.

## Result

| Check | Observed result |
| --- | --- |
| Final host ASan/UBSan metadata | 13,492 scenarios pass, zero live owners/bytes |
| ESP32 SDK6.0.2/Xtensa/QEMU metadata | 13,492 scenarios pass, ILP32 field is unsigned and positive |
| Public header entry order | 12 C/C++ permutations pass on host and in the native build |
| Original-header shadowing controls |Two host compile probes fail as expected |
| Host packet/ownership regressions | 47,166 scenarios pass |
| Independent original PCM | 31 streams, 434 packets, 738,560 bytes; max 0 at unchanged bound 2 |
| Exact original relations | All 14 pass |
| Exact source generator | 17 tests pass |
| New metadata protocol |Seven pure tests pass, including diagnostic rejection |
| Clang-Tidy | 25 units, 306 warnings, zero errors |

The metadata fixture covers 105 distinct rate values, including zero, powers and
neighbors, ordinary audio rates, alternating patterns, both sides of INT32_MAX
and 0xffffffff. Four profiles vary channels 1/2/255/4, valid block sizes 64–8192
and signed bitrate hints. Both zero-size allocator policies, every identification
byte prefix, exact error classes, duplicate/order checks, double clear and fresh
header recovery are covered. Initial info allocation failure returns OV_EFAULT.
Both time-function branches and the -1 sentinel are checked using a manually
constructed read-only vi context; no DSP initialization is performed.

This finite matrix does not enumerate all 2^32 rates. The implementation uses
checked unsigned assembly and a type that can represent the complete nonzero
uint32 domain without a top-bit cap or negative storage.

## API and source selection

The public rate member uses `native_xiph_sample_rate_t`: unsigned long when
long is 32 bits, original long otherwise. All original struct offsets, size and
alignment are preserved on the tested targets. Source signedness is explicitly
extended on ILP32/LLP64; consumers must rebuild with matching headers. Existing
signed-long binaries and `%ld` rate formatters cannot interpret newly accepted
upper-half values correctly. This is not an unchanged source API.

Two checked 16-bit reads assemble the identification rate, keeping valid
0xffffffff distinct from the 32-bit reader's -1 EOP result. Zero remains invalid;
version/channel/block/framing behavior and signed bitrate hints are unchanged.
Prefix lengths 0–6 retain OV_ENOTVORBIS, 7–10 OV_EVERSION, 11–29 OV_EBADHEADER.

The generated public overlay contains the owned codec.h and byte-identical
upstream copies of vorbisenc.h/vorbisfile.h. Their quoted sibling includes must
select the same codec.h. CMake exports only the overlay public directory, and
the active metadata/packet/comment host drivers use it. Compiler dependency
records confirm the overlay instead of the original signed header. The two
negative host controls deliberately reverse that order and reject the mismatch.

All 116 original baseline files remain unchanged. The materializer now records
35 exact edits, 11 changed C units plus one public header, four private headers,
three public overlay headers and 135 generated files including PORTING.json.

## Native metadata gate

Nine actual commands retain SDK identity/cleanliness, build, dependencies,
symbols, merged image, QEMU and post-run SDK checks. All 37 library/fixture/probe
translation units compile, including 12 C/C++ entry-order probes. The runtime
reports long/rate width 32, info size 32, alignment 4, rate offset 8 and unsigned 1.
The strict reader accepts exactly five ordered events with the pinned identities
and count. No watchdog, heap, assertion, stack or timeout diagnostic is removed.

Watchdog and both IDLE checks remain enabled. The independent metadata worker
uses normal priority 0 time slicing on core 1, coordinator core 0 and stack 16384.
Production task bindings and priorities are unchanged. Reported minimum free
heap 253216 and remaining stack 14540 are observations of this isolated metadata
fixture, not radio/physical performance or a general stack bound.

The executable calls identification/comment and granule-time APIs only. It does
not execute setup parsing, DSP initialization or audio packet decoding. Decoder
symbols can remain through registry/export-bundle references; their presence is
not treated as execution. Encoder/convenience-library full-rate support, native
audio PCM, hardware rate support and production integration remain unqualified.
The older packet/DSP/amplitude deferrals are unchanged.

## Host and analysis scope

The original31 PCM comparison remains unshifted and unnormalized; no trim, gain
fit, resampling, reference replacement or numerical-limit change is applied.
The 47,166 host scenarios include arena 23, original packet 27875 and synthetic/
no-work 19268. This is a host PCM result, not a new native packet target gate.

Clang uses actual Xtensa types and the owned overlay for22 library plus three
metadata units. All306 warnings are retained. The new signed-rate narrowing
diagnostics occur in encoder-only paths; they are not newly qualified. The SDK
build retains five inherited GCC warnings under the previous narrow adaptations.
No suppression or assertion policy is relaxed.

The host captures use port manifest5eaf..., before a stale README phrase about
unchanged types was corrected. The native capture uses current b9cc.... The
equivalence record proves that only README.md and its manifest changed: every
implementation/header byte is identical. Both materializations are checked.
The first metadata capture precedes two additional unsigned-granule assertions;
the final host and native captures use the same final fixture.

## Evidence and reader corrections

- Base manifest: `897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
- Current port: `b9cc3c829a816ef8f1a283e23a5b9cc1a45214e9eee541e85560858ed70b0104`.
- Host port: `5eaf91336853646962c77e729d3acb95b668ea64f29bd07607fe11234c2551e5`.
- Generator: `ab969373a3b105c44cdce1d74fdc83dae66ec0576565aee089a2f489cd3ab6b5`.
- Final metadata fixture: `3f843a6d41b0dfa717f992fe96e341e467df2eb60f8c0c8c777fc16973411276`.
- Archive: [captures.zip](captures.zip),14,434,748 bytes /2,339 members.
  SHA256: `4ac7434d18588228d6e49f1880760b9ced2aa00b305847618d7a8e1f668a7dae`.
- Archive manifest: `e46c6bb19eebfc1b7f856b0b71846a84f4f35eeed931342dc6c0547338ff7148`.
- Corrected local verifier: `b96744b9b3f6b455ae20300c6848b680e7a15d31ba92e6afda3b46d1e14ed241`.

The immutable archive also retains the initial verifier. Offline replay found
three reader issues: one transcribed hash, Windows CRLF text parsing in config/
symbol views, and reuse of the generated-path variable in a later tool loop.
The [exact correction record](publication/reader-corrections.json) reconstructs
only those edits and proves the archive, qualification data, diagnostics and
numerical limits were unchanged. All four rejected verification attempts and
the final PASS are retained in [publication/](publication/). No failing runtime
case or diagnostic is hidden to obtain that PASS.

Use the corrected [repository verifier](../../verify-vorbis-xiph-rate-checkpoint.py),
which imports only pinned trusted local receipt/PCM/protocol readers and never
executes archived code, a compiler, SDK or decoder:

```text
python -B tests/verify-vorbis-xiph-rate-checkpoint.py tests/results/vorbis-xiph-rate-20261026/captures.zip
```

It rechecks all members/transforms, actual commands and dependencies, complete
original PCM, header ABI controls, raw native protocol/configuration and Clang
streams. Qualification is true for host/native metadata and host PCM; native
audio, deferred gates, encoder/convenience rate, production and physical scopes
remain false.
