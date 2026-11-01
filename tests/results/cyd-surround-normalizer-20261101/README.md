# Shared envelope for all logical speaker channels

The separate `native_audio_normalizer_process_multichannel_block` API observes
and soft-limits all1–8 logical channels with one shared envelope/time advance
per frame. It reuses the existing gain target, Q12 arithmetic, limiter and
configuration. Invalid/null/overflowing geometry leaves samples and DSP state
unchanged. The original stereo/frame/block APIs are unchanged; C3 callers
continue to use their existing path. The new API is not yet selected by CYD.

The before-change characterization reproduces the first-two-only behavior:
72 enabled multichannel configurations differ from an all-channel envelope,
while disabled processing and C1/C2 remain exact. The final API has zero
differences over128 streams /2359296 samples, all1–8 channel counts, four
configurations and partitions1/127/128/511. Inputs include full-scale signed
endpoints, quiet front channels with an active later speaker and different
signals on every channel. Canaries and invalid-geometry/state guards pass.

The oracle uses independent public stereo AudioNormalizer instances: each
instance receives its source channel plus the original frame's maximum-
magnitude sample. This gives every instance the same detector/envelope clock,
without reimplementing private gain/limiter arithmetic. Actual output uses one
normalizer instance and the new C adapter. Both run under ASan/UBSan/leak checks.

The existing three-backend CYD normalizer regression also passes unchanged:
PDM239, continuous DAC240 and legacy DAC239 packets, including immutable,
unaligned and wider legacy input, settings/reset, split identity and lifecycle.
This is host DSP qualification, not physical DMA, target timing, full radio
resources or completed surround playback integration.

Reports are unchanged copies of their original local captures:

- `baseline-report.json`: `.build/cyd-surround-normalizer-baseline-20261101-02`.
- `report.json`: `.build/cyd-surround-normalizer-20261101-01`.
- `legacy-report.json`: `.build/cyd-surround-normalizer-regression-20261101-01`.
- `history/initial-baseline-report.json`: original first baseline non-PASS.
  Its compiler/test children returned0, then a duplicate-key error in final
  report printing caused the outer failure. The corrected fresh02 is separate.

Exact source hashes, process identities/statuses and stream hashes are retained
by the new runner. Native binaries/full local source snapshots stay ignored;
these public reports do not independently replay omitted captures. The legacy
runner records its normal original host report rather than a full PID ledger.

```powershell
python -B tests/run-cyd-surround-normalizer.py --output .build/<fresh-capture>
```
