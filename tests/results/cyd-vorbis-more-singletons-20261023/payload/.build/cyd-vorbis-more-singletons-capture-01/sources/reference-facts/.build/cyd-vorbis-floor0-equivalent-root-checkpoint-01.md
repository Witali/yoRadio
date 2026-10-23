# CYD floor0 equivalent-representation checkpoint, 2026-10-23

The additive six-case experiment completed on the standalone CYD raw-packet
project. Every new target PCM stream is byte-identical to its original floor0
case. Changing this representation did not resolve the observed error in these
fixtures. The complete 31-case numerical comparison remains NONPASS against the
unchanged project criterion of at most 2 S16 LSB. That engineering criterion is
not a normative Vorbis tolerance.

## Inputs and independent reference

The six additions preserve the original even-order6 and odd-order5 cases at
all three block-size pairs. Their lookup2 minimum changes from zero to 1/16,
and every unsigned multiplicand decreases by one. Delta remains 1/16; order,
dimension, sequence, wire words and reconstructed LSP values remain identical.
Identification, comments and audio bytes are unchanged. Only necessary setup
bits and their carrier CRC change.

Generation completed with actual terminal0 (`e6cf3a`). The separate bounded
raw-bit/Fraction/CRC witness completed with terminal0 (`4f8a23`), report
`6847029d693a61b17690d1798b4c5e8c5d1c3c19574afc20932a3e0fe4ba84b9`.
It checks all six pairs and 84 packets, plus three construction controls.

The actual 12-case host campaign completed with exit1 (`ffd30a`), report
`804a46f29eed98ab6e3c71a5aff79d11546d1efd87dddea8f6fad7f7cee2ce17`.
Xiph accepted all twelve cases, and all six original/addition PCM pairs were
byte-identical. Native FFmpeg refused all twelve lookup2 setups. Its 24 child
receipts and the original dual-reference NONPASS are preserved. Independent
recorded-reference qualification completed with actual terminal0 (`2b002d`),
report `29ca7992d6deed8766f61ec5fc79ac3b5108bf7ec0dd12d1732df514af65881c`.

## Actual CYD capture and numerical result

The first 25 descriptors and all raw inputs were retained, followed by the six
additions. The complete model derives 31 cases, 434 packets, 738560 PCM bytes,
964 protocol events and mask2147483647. The original source-preparation README
predicted 734464 bytes; that prose arithmetic error is retained. Actual model,
materializer, independent C-header recovery and target all require 738560.
Five materialization controls reject incorrect capacity/totals/raw ID/offset/
descriptor order. No smaller subset substitutes for the complete capture.

The actual SDK/QEMU capture completed with terminal0 (`d6f0b8`), report
`6f7f346df8c2185776fa8727977e363c284f8bdc459ef90c5ed28affc3b6d81d`.
All nine owned commands ended0. All31 raw open/decode/close cases completed,
including434 packets,738560 persisted PCM bytes and964 protocol events. This
uses the exact reviewed CYD setup source, ESP-IDF6.0.2, Xtensa ELF94/240MHz,
coordinator core0 and decoder worker core1. Production task settings did not
change. No board, COM port, network audio or production firmware was used.

The root's direct comparison completed with terminal0 (`cdb1b5`), witness
`ad097a2d041164267d99e95c9b884e6f41b69cad68899fc4b8a388e8509e3de9`:
all25 earlier PCM files and775 case-specific events remain byte-identical;
all six added PCM files equal their corresponding original floor0 output.

The full numerical comparison completed with exit1 (`bd03a3`), report
`ae859a2ec8fa83ceab5204ccea2a2a3f3898f55484de6395fddb7d705f57c54d`.
All31 cases were measured without an input error. The six addition maxima are
40664/1649/40664 for even6 and65535/65535/65535 for odd5, matching the originals.
The four earlier wide lookup2 failures also remain. All14 declared Xiph
relations pass; the target still fails its two wide sparse/dense relations,
while all six original/addition floor0 relations pass. Neither the complete
corpus nor the earlier25-case projection passes the numerical criterion.

## Separate public-formula diagnostic

A separate owned binary64 calculation reads the six original raw setups and
all84 audio packets, reconstructs exact LSP/amplitude/residue fields, and
evaluates the public floor0 equations. Its actual terminal0 is `4acca6`, report
`76c5c726c076b0f75464d627d850746b838c02c852cc827de23cb34bb1f77be7`.
Five own-formula sanity-control groups pass. Of2688 active-bin observations
across168 channel-packets,147 request positive dB under these ideal formulas.

The report separately illustrates a conditional positive-dB unity clamp using
the same ideal requested dB. Public Tremor's integer mapping, rounding and
lookup path were not evaluated. This calculation launches no decoder and
produces no PCM; it establishes no cause of the observed target error and
attributes no behavior to the opaque backend. Its formulas and source links
are recorded in the exact preparation retained here.

## Remaining scope

The owned floor0 field-publication unit, actual public-Tremor numerical
comparison, remaining singleton/width/mapping coverage, other G1–G8 gates and
radio integration remain open. Existing Ogg/reset/allocation-failure deferrals
are unchanged. Original failures, partial evidence and policy remain intact.
