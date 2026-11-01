# CYD output-owner Opus header gain, 2026-11-01

The actual shared CYD PCM reader and all three real backend producers now
combine Opus header calibration with the existing rounded Q15 volume/balance
coefficients before wide mono mixing and final S16 rounding/saturation. The
adaptive normalizer remains unchanged and precedes this additional output
calibration. This is an application integer-PCM playback policy, not a claim
of numerical equivalence to pre-quantization libopus floating synthesis.

The output-owner API is `native_audio_output_set_header_gain(int16_t gain_q8)`.
The caller supplies ordered per-packet signed Q7.8 metadata after configuration
and before writing PCM. The setter computes a factor only when metadata changes,
validates it before replacing the cache, and stores no PCM or borrowed pointer.
Startup, discard, flush and pause use identity gain. Zero gain uses the previous
arithmetic verbatim. All layouts retain the current signed LE8/16/24/32 to S16
projection, first-two-channel mono mix, resampling and DAC error diffusion.

Nine original local campaigns are preserved without rewriting their bytes:

- Three pre-change baseline suites supplied by the coordinating agent.
- Initial new-gain campaign `01`, passing all three producers with five math
  refusals. Its factor guard was subsequently strengthened.
- Campaign `02`, a preserved terminal **NONPASS**: adding a finite `DBL_MAX`
  libm fault exposed a setter that accepted an unusable factor. The five earlier
  nonfinite/nonpositive fault cases already passed in campaign `01`.
- Campaign `03`, fresh terminal PASS after bounding the prospective factor for
  two full-scale channels before publication. All three producers pass 13,824
  independent Decimal vectors, 192 ordered stream packets, 65,536 changed-gain
  transitions with same-gain reuse and six transactional math refusals each.
  Each backend additionally has 58,537 exact trace samples independently
  checked using Decimal at both 80 and 120 digits. No tolerance was introduced.
- Three final zero-gain regression campaigns `02`, with unchanged assertions,
  inputs and expected arithmetic. Runner changes only wire the new shared
  header/include path, libm linkage and source capture.

The baseline and final legacy result strings match exactly: each backend keeps
5,801,300 gain arithmetic cases and 375 producer cases; normalizer counts remain
239/240/239 packets; layout counts remain 1,359/1,358/1,358 stream cases with
721,152 conversion checks. PDM retains 1,278,222 interpolation checks and its
previous bound of two S16 LSB against the rational tap reference.

The new suite exercises positive gain with low volume (including +48 dB and
volume 1), mute, negative/extreme gains, balance extremes, opposite-sign
cancellation, immutable unaligned input, all supported widths, mono/stereo/
wider layouts, same-gain caching, consecutive different gains, split writes,
unchanged normalization history, post-refusal rendering, short/failed writes,
failed pause and failed PDM tail flush. It builds with ASan, UBSan,
float-cast-overflow checks and leak detection. Original regressions retain
their previous sanitizer configuration. The unchanged normalizer reference
runs one frame at a time while production uses bounded block scratch.

Driver calls are capture/fault seams. No physical board, DMA timing, target CPU
performance, SDK build or complete production task-pipeline selection is
claimed here. The task pipeline must separately prove that queued packets keep
their own gain metadata across chained links and generation changes.

`captures.zip` contains byte-identical original reports, logs, generated C and
source snapshots, deduplicated by SHA-256. Synthetic arithmetic vectors/traces
contain no decoded media. Host ELF executables and objects remain local and
are listed only by hash and size. No executable or firmware is published.

Run `python tests/results/cyd-header-gain-output-20261101/verify.py` to verify
the frozen evidence as data. Add `--require-current` to also compare the final
source bindings with the current worktree. Historical verification does not
require evolving production sources to match this campaign forever.

The gain law and requirement to include other gain modifications are from
[RFC 7845, section 5.1](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1).
The RFC does not prescribe the ordering of an application adaptive normalizer;
the existing detector, Q12 amplification and limiter are intentionally retained.
