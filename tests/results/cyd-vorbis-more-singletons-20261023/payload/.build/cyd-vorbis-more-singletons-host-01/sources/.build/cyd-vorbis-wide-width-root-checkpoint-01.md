# CYD wide lookup2 width checkpoint, 2026-10-23

All12 complete raw cases decode on the standalone CYD project. Their numerical
comparison remains NONPASS: every case has maximum signed-S16 error65535 against
Xiph. None of the four declared three-width equivalences or six source-derived
sparse/dense equivalences holds for the target. All ten hold for Xiph. Changing
the tested quantization width alone does not resolve this finite-corpus error.
No cause is attributed to the opaque backend and no production source changed.

## Exact additive controls

The first four cases are the unchanged dimension16 lookup2 sparse/dense cases
with sequence0/1. Eight additions encode the same unsigned multiplicands at
width9 and16 instead of2. Minimum−1, delta1, dimension, Huffman codewords,
sequence, decoded vectors, identification, comments and audio bytes remain
unchanged. Only necessary setup encoding, carrier lacing and CRC change.

Actual generation completed with terminal0 (`8fff80`); the separate bounded
raw-bit/Fraction/CRC witness completed with terminal0 (`713a8e`). It checks all
original quantization rows, including unused rows, exact vectors and unchanged
surrounding fields, plus five construction controls. The complete comparison
matrix contains original4 followed by width9four and width16four. Additions do
not replace any earlier25/31-case failure.

## Actual independent reference and target

The actual12-case host campaign completed with exit1 (`a39fb8`), report
`eb615bfa54da44b98c4dd9d4ea31dcf6a2db393ceb40631bf90e0134fdc9ab7f`.
Xiph accepts all12 and produces identical PCM in each declared width triple.
Native FFmpeg records12 lookup2 refusals; the original24 child receipts and
dual-reference NONPASS remain intact. Recorded-reference qualification completed
with actual terminal0 (`803a60`), report
`45130a3de50aa41212f30ef41fd071b0f77aea13899575a88842767ed29f37f3`.

The separately reviewed preparer requires that actual qualification and its
terminal0 before publishing the runnable controller. It derives12 cases,
168 packets,337920 PCM bytes,375 protocol events and mask4095. Five independent
C-header recovery controls reject incorrect capacity/totals/raw ID/offset/order.
The original caller/protocol and production task bindings are unchanged.

The actual CYD SDK/QEMU capture completed with terminal0 (`977a73`), report
`7913274b872d5748ed50952e269a85b16a66929b6827824badb7a6a8524653ba`.
All nine owned commands end0. The complete12-case raw open/decode/close capture
persists every expected PCM byte and validates every protocol event, canary,
packet consumption and core1 decoder observation. Profile: ESP-IDF6.0.2,
Xtensa ELF94/240MHz/SMP, coordinator0 and worker1. This is a fixture project,
without a physical board, COM port, network audio or production firmware.

## Complete numerical comparison

The actual numerical measurement completed with exit1 (`51cf95`), report
`36b62eda98e90a990f7ab2f9b4933b3bea8b53aa6bbc77d7243bd08ef762601b`.
All12 cases were measured without an input error, using complete recorded Xiph
WAV/framemd5 and complete target PCM. All12 maxima are65535. Every target width
triple and sparse/dense pair fails; every corresponding Xiph relation passes.
The extra six shape relations follow from the two original predeclared pairs
and four independently qualified width triples, not from fitting target output.

The unchanged project engineering criterion remains maximum2 S16 LSB with
complete zero-lag L/R data, nonzero channels/transitions and all relations.
No trim, gain fit, time shift or channel swap affects qualification. This is
not a normative Vorbis tolerance. Full12 NONPASS is preserved.

The optional historical comparison validates the full previous25-case capture
before comparing the unchanged four raw inputs, packet geometry and complete
PCM. All four are byte-identical to that prior target result. This diagnostic
cannot override the complete12 numerical failure. A supplemental root witness
also records equality with those four cases in the previous31-case capture.

## Remaining scope

These finite tests do not qualify general wide lookup2 or full G6. The owned
parser/public-vector unit remains separate from an actual decoder numerical
result. Remaining singleton/mapping formats, floor0, other G1–G8 gates, radio
integration and physical acceptance are open. Existing Ogg/reset/allocation-
failure/private-owner deferrals remain unchanged.
