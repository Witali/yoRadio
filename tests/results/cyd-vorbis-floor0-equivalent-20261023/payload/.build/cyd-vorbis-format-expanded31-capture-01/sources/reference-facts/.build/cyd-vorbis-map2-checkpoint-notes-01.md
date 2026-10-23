# CYD Vorbis codebook setup checkpoint, 2026-10-20

The public setup repair now consumes lookup2 multiplicands for every original
entry, retains active wide rows in compact used-entry order, and publishes the
original mapped value for a single active codeword on both one-bit branches.
The canonical CYD setup changes from SHA `d23fd5cb...` to `6b36d56b...`.
Vendor ABI, synthesis/MDCT/output arithmetic and the production radio integration
are unchanged. C3's corresponding source proposal has not been applied or run.

## Actual target evidence

Both standalone SDK6.0.2/Xtensa captures completed all nine owned commands with
exit0. Coordinator0 and decoder1/priority3/configured stack16384 are retained.

| Capture | Cases | Raw packets | Actual PCM16 bytes |
| --- | ---: | ---: | ---: |
| Checked17 | 17 | 238 | 398080 |
| Corrected checked25 | 25 | 350 | 623360 |

Every case retains complete public open/decode/close, packet consumption,
metadata including primer, overlap sizes, output canaries, channel nonzero
evidence and all emitted PCM bytes. This is a capture success, not a complete
format or numerical qualification.

Three separate source controls restore only one old branch. Each has seven
zero-exit owned commands and a zero-exit QEMU process, followed by the exact
expected public open rejection. The controller correctly returns1/NONPASS.
Every preceding protocol event and PCM byte equals the fixed capture prefix.
No control has a panic, timeout or interruption.

| Control | Failing case | Successful preceding packets | Preceding PCM bytes |
| --- | --- | ---: | ---: |
| Packed unused-row read | 6, sparse explicit D4/seq0 | 84 | 168960 |
| Wide active-row read | 8, sparse explicit D16/seq0 | 112 | 225280 |
| Mapped singleton | 12, single explicit D2/seq0 | 168 | 337920 |

## Numerical results remain NONPASS

The separate comparisons measured every case against its independently qualified
Xiph WAV, using every original zero-lag L/R S16 sample and packet. The engineering
bound2 was declared before measurement; it is not a normative Vorbis tolerance
and was not raised. No shift, trimming, gain fit, channel swap or resampling was
applied. The original17 and additional8 host campaigns retain their actual
dual-reference exit1 results: Xiph accepts all cases, while FFmpeg native refuses
ten and eight lookup2 cases respectively. No aggregate host command is invented.

- Original books8, mapped single/twin4 and floor1/residue0 controls3 have maximum
  absolute error1. Both new single/twin PCM equality pairs hold exactly.
- Wide D16/seq0/1 sparse and dense cases4 have maximum error65535, and both
  expected sparse/dense PCM equalities fail. Setup acceptance is repaired, but
  wide PCM remains unqualified. The public-source audit found no concrete new
  setup correction; the opaque backend's exact behavior has not been diagnosed.
- Floor0 even6 cases have maxima40664/1649/40664; odd5 has65535 for all three
  block pairs. These six original failures remain. Public zero-minimum shift,
  positive-gain saturation and Bark stepping are hypotheses, not proven causes.

Full25 and the explicitly declared books16 subgroup are both NONPASS. The
archive verifier independently recomputes signed-S16 error maxima, mismatch
counts, squared errors and the eight relations from retained PCM/WAV bytes.
Its integrity result must not be read as numerical acceptance.

## Preserved history and reproduction limits

The original paired-vendor case6 heap panic is distinct from the checked parser's
graceful baseline rejection. The obsolete unused-symbol gate, first25 build's
capacity17/PCM-total macros, and first numeric adapter's framemd5 stereo-label
error are retained as failed history. The corrected table changes only its two
macros to25 and623360; independent recovery checks model, descriptors, declared
capacity and all125 arrays/75 complete raw payloads, including exact corruptions.

`manifest.json` binds original paths, frozen snapshots, actual command receipts,
logs, build context, link maps, source versions and PCM/WAV bytes. Large retained
files are losslessly compressed; tools, SDK installations and target binaries
are hash-only omissions, with actual64-byte ELF headers retained. This is an
evidence bundle, not a complete SDK rebuild image or production firmware handoff.
The archived `README.md` describes the original packer proposal; this document
records the root-owned checkpoint. Run `python -B verify.py <bundle-path>` for
read-only offline verification. No installed SDK, QEMU or FFmpeg is needed.

Remaining work includes a unit test of our book/floor0 publication followed by a
pinned public Tremor decode_map/curve seam, equivalent-LSP representations,
sparse-single/map1-single/wide9–16-bit cases, independent C3/RV32 qualification,
the remaining G1–G8 gates and radio integration. Deferred Ogg/EOF/reset/OOM and
AAC work was not resumed. Physical acceptance remains open at the user's request;
no board, COM port, flashing, reset, network target or physical audio was used.
