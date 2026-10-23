# CYD mono/stereo and mapping21 checkpoint, 2026-10-23

The complete finite corpus passes the predeclared project PCM criterion on the
isolated CYD bridge: all21 cases differ by at most1 signed-S16 LSB from each of
Xiph libvorbis and FFmpeg native Vorbis, within the fixed2-LSB limit. All42
target/reference comparisons retain every sample and packet boundary. This is
finite regression evidence, not a normative Vorbis tolerance, fullG6 approval or
production radio integration.

## Corpus and existing independent references

The21 original cases contain9 mono and12 stereo streams. Mono/stereo pairs cover
8000,11025,12000,16000,22050,24000,32000,44100 and48000Hz; the remaining three
stereo cases cover coupling quadrants, two submaps with swapped mux and residue2.
Every case contains14 complete raw audio packets, an empty primer and all four
short/long transitions. Each actual channel produces7040 frames. The complete
corpus is294 packets and464640 PCM16 bytes. Mono remains one channel.

Original and canonical construction retain identical matrix/construction bytes
and all105 raw/header/carrier files. Matrix SHA256 is
`30fad94ec85727030a415f33c544041ed225aae97397b09584a534f7c2636d37`.
The committed generator-reproduction record and complete109-file original and
canonical inventories are retained. Construction/readback uses generator
helpers; it is not an independent codec parser. Earlier failed readback01 remains
historical evidence alongside successful readback02.

The existing mono21 reference campaign already completed42 strict decoder
children successfully,21 per implementation. Its original host report is
`ab80560ca5a1a6d01acdac07508122125bbb7f6597eafb5a94f1a454b31b7abd`;
the reviewed qualification is
`c31a87de53327cb0e43215f92339b07fd64c48ba57dbde8778328f298b9f5684`.
All42 recorded receipts/logs/WAV/framemd5 streams, raw inputs, metadata and frame
counts were revalidated. Both references agree within1 LSB in every case. These
are existing actual child results; no new reference process or aggregate campaign
is claimed. Other campaigns' native refusals and NONPASS remain unchanged.

## Actual SDK/Xtensa capture

The source-only runtime preparations01 and02 remain immutable. A missing
allowance for the legitimate module `__doc__` attribute was found before runtime
materialization or SDK execution and corrected only in successor02. Preparation02
readiness is `6be5847a47fc9c2af2046cb5a20738ee3d439805db78a48d52180c5cdf7f2c26`.
All30 host protocol controls passed in an actual retained process.

Actual materialization verified all original raw bytes, the complete reference
binding and105 restricted-C arrays, including63 full raw-payload arrays and five
recorded corruption controls. Preparation SHA256 is
`b94c9d6e0a2659e174bf9e8f2de422d9241b99e12297df9aab644fc244f7d5c4`.
The full contract is
`8b62de9035798c6086d52259c68e26071e96e925d4ec569b4c448f96f70abe0b`;
the header is `b7dfd4ed734c1861eb0a1945e8d3a18fee23a75b5a3657799a43f7cfb78ed23b`.

SDK6.0.2 at `7101770dc6db2667b3c477cc31365dd1acd6db4e` compiled and linked
the unchanged reviewed CYD setup/output bridge with the complete caller. The
actual profile is ESP32/Xtensa ELF32 machine94,240MHz,SMP, coordinator core0,
worker core1/priority3/configured stack16384. Canonical setup SHA remains
`6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c`.
The caller validates actual public rate/channels/bits, complete consumption,
ample guarded output, the empty primer and nonzero output on each real channel
for each transition. It does not duplicate mono output or probe private handles.

All nine owned target commands reached ordinary terminal0, including QEMU.
Actual capture completed21 cases/294 packets/464640 PCM bytes/654 events,
case mask2097151, with no compiler warnings or errors. The raw protocol and all21
persisted PCM streams are retained. Actual direct tool session46039 ended0 in
chunk`bfffd4`; the direct terminal was recorded from that completion.

- Controller: `77ceba3cc8ced16159e90316158480f778c74b5d1f7898c17f222180ee692574`.
- Capture report: `06bd8a60cef8d2f49bc4df839630a405e49823061be02f831d36ef5fd0655daf`.
- Direct terminal: `fa2bfd189ac1b20882c2c31d57ec1b0b866f2141db978cd08a6783bbdc2cec29`.

## Complete numerical comparison and harness correction

The2-LSB policy was fixed before target measurement and remains byte-identical:
`219ec8d967e45536cbddf926e932e8647693d3e1320a75d562a1cd913e2e9119`.
It requires every sample to meet the bound against both existing references,
all21 cases/42 comparisons, correct actual channels and complete transitions.
This project criterion is not a standard-mandated numerical tolerance.

Numeric preparation01 readiness
`e5df77c9c0b73f327b693a9ad7f76054ccc55c9fc563107778ad4fb06dea2748`
and its successful29-control run are preserved. The first actual measurement
exited1 because the capture report stored Windows backslashes in variant source
keys while the verifier used a forward-slash literal. Its report
`b87fd1d02fdf2fd532dd5edce71d3bc311cfe57fc4849a8937e3d690a1daad18`
is `INPUT_OR_MEASUREMENT_REJECTED` with a KeyError, empty cases and
measurement/reference-comparison false. This is an input-check failure, not a
decoder numerical NONPASS. It occurred before comparison and persisted-PCM
validation, after hashing command logs containing PCM_HEX. The original attempt,
receipt and all logs remain exact.

Immutable numeric preparation02 changes only safe variant-path key
normalization and adds10 host controls for real Windows/mixed paths, aliases,
unsafe paths, malformed hashes and missing/wrong setup identities. All identity
checks remain; metrics, policy, comparator and the existing29 controls are
byte-identical to01. A separate source-only audit checks the other729 snapshot
paths and actual metadata schemas. Final readiness is
`0f7ce1d76f5a3541fbe7f7e798fe1eca7b85d27f57e6f8ac44bdd74aa4ea0950`.

All39 actual host controls passed0 (`da6386`,0.556s). Their receipt is
`85b52654053c5a75b40bb75587d8fe14b606bd012211a5d7d47f3ce4fee60657`.
They include signed-S16 extrema/full65535 errors, complete odd mono lengths,
last-packet errors, fixed diagnostic lag, missing/subset/channel/transition and
both-reference2-versus3 policy controls.

The final actual comparison completed0 (session65490, terminal chunk`d47eea`):

- Measurement report: `aeb88a8c01a10170880c33fd21142f48839920c30f28f3746293e501eceada9e`.
- Actual wrapper receipt: `1155ac190a896fdff9220ad0ca295e360af98da8d9f6d3b7cd8384c5c93a6d09`.
- Result: `BOUNDED_CORPUS_PCM_QUALIFIED`; all21 cases have max1 against Xiph and
  max1 against native FFmpeg. Both-reference policy result is true.

Every raw sample, packet offset and real channel is compared at original zero
lag. No trimming, fitting, gain, shift, swapping, resampling, padding or mono
duplication is applied. Diagnostic alignment does not change acceptance. Full
metrics retain clipping, signed errors, histograms and transitions; these
constructed signals are not a representative listening or performance corpus.

## Archive boundaries and remaining work

The archive retains original source versions, actual process records, full
inputs/output and complete numerical metrics. SDK/tool/library/app binaries are
hash-only omissions with actual ELF header identity. Only explicitly identical
shared entries may come from the pinned committed CYD map2 dependency. Earlier
map2/singleton/floor0/wide campaigns are record-only and are not replayed or
requalified by this checkpoint. The archive is not standalone.

The prior wide, floor0 and D16 sequence1 regressions remain open with their
original fixed2-LSB NONPASS results. Preferred-zero singleton target coverage,
other format coverage, callback/lifetime/concurrency gates and production
radio/resource qualification remain. Deferred Ogg/EOF/reset/OOM and AAC work is
untouched. No physical device, COM/flash/reset, production radio application or
audio output was used. Task affinities and production firmware are unchanged.
