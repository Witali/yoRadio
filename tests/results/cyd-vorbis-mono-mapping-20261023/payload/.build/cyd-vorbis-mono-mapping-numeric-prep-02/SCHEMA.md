# Numeric21 measurement and offline replay interface

Pure helpers are ordinary imports: `mono_metrics.compare/alignment`, unchanged
`pcm_metrics.compare/alignment`, `policy21.bounded_policy/whole`, and unchanged
`recorded_qualification.decoded_pcm` with `carrier.py`. They launch no process.
Mono/stereo dispatch must use the verified actual channel count1/2. The generic
`pcm_metrics.errors` has no stereo assumption; its byte unpacker does, so mono
uses its own `samples` and never calls the stereo unpacker.

Top-level completed report fields include:

- `measurement_completed`, `actual_reference_compared`, `target_platform_verified`.
- `complete_target_cases=21`, `complete_target_packets=294`,
  `complete_target_PCM_bytes=464640`, `complete_reference_streams_verified=42`,
  `complete_target_reference_comparisons=42`.
- `cases`: exact original21 order; no missing/duplicate/relabelled cases.
- `policy`: fixed predeclared2 LSB, all fitting/application flags false,
  per-reference numeric/nonzero/transition flags and `bounded_by_reference`.
- `bounded_corpus_pcm_qualified`: requires both reference classifications true;
  `result` is `BOUNDED_CORPUS_PCM_QUALIFIED` or `BOUNDED_CORPUS_PCM_REJECTED`.
- `original_dual_reference_passed=true` and
  `original_dual_reference_scope=only-existing-mono21-campaign`.
- `previous_unrelated_NONPASS_reinterpreted=false`;
  `no_predeclared_metamorphic_groups=true`. No fabricated relation rows.
- Actual target report/terminal/runtime preparation SHA identities and complete
  `inputs` size/SHA facts. Failure preserves `measurement_completed=false`.
- `passed`, `numeric_reference_qualified`, `format_corpus_qualified`,
  `format_conformance_qualified`, `full_G6_qualified`, `physical_device`,
  `production_radio_integration` remain false; the bounded result has finite scope.

Each case row has `case`, `id`, `rate`, actual `channels`, `bits=16`, `frames`14,
`packet_bytes`14, full `pcm_bytes`, `packet_offsets`15, `reference_id`,
`references`, `original_reference_cross_comparison`, `original_reference_metadata`.
`references` has exactly `vorbis` and `libvorbis`. Each contains `comparison`,
`alignment_diagnostic`, `reference_transition_nonzero`, `target_transition_nonzero`.
Both transition dictionaries have SS/SL/LS/LL and arrays of exactly actual channels.

Mono comparison has `zero_lag_direct_mono`, stereo keeps unchanged
`zero_lag_direct_LR`. `policy21.whole` selects the appropriate existing key.
Both comparisons retain `byte_equal`,7040 `frames`, integer-LSB `unit`,
`channels` of length1/2 and all14 `packets`, including zero primer.
The mono-only `channels_count=1` is explicit. Each packet has `packet`,
`byte_offset`, `bytes`, `frames`, `all_samples`, and1/2 `channels` statistics.
Whole statistics include signed extrema/max absolute error, full histogram,
sum/squared sum/mean/RMS, mismatch sample/frame/channel, clipping and nonzero
counts. Mono mismatch frame equals sample index/channel0; stereo mapping is unchanged.
Primer extrema are null because it has no samples.

Diagnostic alignment has a single mono channel pair or four stereo pairs, a fixed
interior reference range and the unchanged17 lag candidates for default±8.
`diagnostic_only=true`, `applied_shift_frames=0`, `applied_channel_swap=false`.
No diagnostic minimum can substitute for any primary zero-lag measurement.

For offline archive verification, independently recover complete target protocol
PCM and every packet offset, replay each recorded WAV/framemd5 via exact actual
rate/channels/frame arrays, then recompute both comparisons, diagnostics and
transition counts. Recompute native→Xiph reference comparison too. Call
`bounded_policy` only with all21 complete case rows; no unverified truncation,
mono duplication, padding or invented metamorphic groups. The standalone archive
may relocate stored paths under its declared manifest, while retaining every
original receipt/source identity and the exact policy219ec… unchanged.

Successor02 changes no measurement/report/policy fields. Only variant_sources
input path keys are safely canonicalized before the same exact setup identity
gate. All original actual failure01 and successful controls29 remain separate
provenance; the new root run must use fresh measurement02 and all39 controls.
