# CYD mapped-output host checkpoint, 2026-11-01

The final host campaign passed all three actual CYD output producers: PDM,
continuous DAC, and legacy DAC. Each completed 23,904 static vectors, 384 PCM
packets, five metadata refusal/reset controls, and 106,688 independent oracle
trace rows. Normalizer scratch remains 512 bytes. The original static goldens
are byte-identical between the genuine failure and the successful rerun.
This checkpoint does not select the new layout in the application queue or
qualify a complete production task, physical DMA, MCU throughput, or universal
numeric/codec conformance.

The captures retain the original sequence without rewriting reports:

| Campaign | Original result | Evidence |
| --- | --- | --- |
| `output01` | NONPASS | Decimal precision disagreement before vector generation/host execution; the original oracle lacked the exact equal-channel row-sum identity. |
| `output02` | NONPASS | Real PDM host assertion at static vector 17461: naïve binary64 addition lost the final half boundary. No successful backend is recorded. |
| `output03` | PASS | All three complete producers and all-channel normalizer traces; only `pcm_speaker_mix.h` changes from `output02`. |
| `matrix03` | PASS | Auxiliary public matrix-helper tests, 72 coefficients, 36 impulses and 104 controls. Its own final-S16 and enabled-normalizer acceptance flags remain false. |
| `sum01`, `sum02` | Completed observations | The original provisional extra oracle and the subsequent separately recorded exact rational resolutions remain intact. |
| `classification01` | Completed observation | Thirty remaining ideal-S16 differences localized to independently rounded products. |
| `cost01` | NONPASS | Standalone recursive-tree candidate rejected by GCC's maybe-uninitialized diagnostic. |
| `cost02` | PASS compiler capture | Unused recursive-array slots initialized only in that target diagnostic copy; code/stack observations, no target execution. |

The actual output C is extracted without arithmetic changes from the frozen
production file into three host translation units. Platform driver calls
capture output bytes. The harness compares every complete captured producer
buffer against independently packed PDM, continuous-DAC or legacy-DAC output;
the complete successful logs retain those assertions' result. It covers
unaligned packed signed 8/16/24/32-bit input, one through eight logical channels,
header gain, user volume/balance, split/unsplit packets, enabled/disabled
normalization, immutable read-only input, and metadata refusal/reset behavior.
The real C++ normalizer adapter and algorithm are linked, with sole-owner and
scratch/frame bounds checked by wrappers. ASan, UBSan, float-cast-overflow and
leak checks are enabled in the frozen runner.

The CSV files are the independent post-normalizer/mono-oracle records, rather
than raw hardware PCM. Their equality across producers is authenticated, and
the successful C assertions establish their relationship to captured host
output. The verifier independently regenerates all static vectors, the exact
compiled golden header, the original extracted C units, raw sample projection,
the fixed-settings Q12 envelope/limiter, and each trace's 100/160-digit Decimal
mono result. Of each producer's 106,688 rows, 53,344 have normalization enabled.
This is data authentication and independent selected-case recalculation; it
does not re-execute the archived C/Python/C++ or reconstruct unpublished binary
execution. The original output runner retains source hashes and combined
build/link/test logs, rather than individual compiler process IDs; no missing
process provenance is invented here.

The coefficient formulas are those in [RFC 7845 section 5.1.1.5](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1.1.5).
The public binary64 coefficients are retained. Neumaier accumulation fixes all
nine existing static failures and matches the correctly rounded sum of the
actual rounded products in all 65,376 selected arithmetic observations. This
is an observed finite corpus, not a universal exact-summation theorem. In the
45,504 extra cancellation/extreme cases it still differs from the ideal real
matrix's final S16 on 30 exact-half cases: 28 sign-extreme and two uniform-odd
cases. Exact dot products of the stored weights recover the ideal S16 there;
rounding each multiplication separately loses those boundary bits.

The provisional extra oracle had 50 precision disagreements and 14 additional
exact negative-half labels on which two Decimal precisions agreed incorrectly.
Exact algebra in the public speaker-matrix basis resolves these separately in
`sum02`; neither original campaign nor any existing static golden was edited.
No epsilon, numerical tolerance, coefficient bias, or golden relaxation is
introduced. The original provisional count of 16 remaining Neumaier
differences is superseded by the qualified count of 30 after these extra-oracle
corrections; the old report is still present unchanged.

Standalone classic-ESP32 Xtensa GCC 15.2.0 observes 266 bytes of text/literals
and 80 bytes static stack for the diagnostic Neumaier function, versus 86 and
32 for the naïve version. At eight channels the emitted loops require 57 versus
24 software-helper calls including conversion, multiplication and comparison.
Inlining/linking can change code and stack; these are compiler observations,
not cycle measurements or a claim of real-time throughput. Existing one/two
channel legacy arithmetic remains outside the proposed summation change.

`captures.zip` contains 178 logical files in 74 content-addressed blobs. All
nine original reports, source snapshots, generated units, selected oracle
records, and logs are bound by exact SHA-256 and size. Eighteen complete compiled
binary/object payloads remain local with exact omission identities; none is
redacted into a different payload or declared safe by a semantic override.
The separate lifecycle/FLAC campaigns and earlier six legacy-suite wiring runs
are outside this checkpoint. In particular, those earlier runs are not claimed
as a final rerun on the current compensated-sum bytes.

Run `python tests/results/cyd-surround-output-20261101/verify.py` for frozen data
authentication. Add `--require-current` to require the final bound production
and test sources still match the working tree; omit it for a historical review
after source evolution. Add `--self-test` for contradiction controls covering
unsupported acceptance claims, promotion of original failures, an altered
legacy producer, and an altered enabled-normalizer sample. No build, SDK,
emulator, board, network, or archived program is invoked by the verifier.
