# Checked-only17 measured PCM adapter: source proposal

This separate adapter supports only complete `CHECKED_CORPUS_PCM_CAPTURED`
captures. The paired numeric01 proposal remains unchanged. No actual PCM
comparison or qualification was run in this preparation. Baseline02 is the
historical NONPASS with case6 open failure; it must be rejected before reading
reference or target PCM. No partial extractor, dropped case or fallback exists.

`pcm_metrics.py` is byte-identical to the frozen original core, SHA256
`a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f`.
`adaptation.diff` and `source-relation.json` record the exact adapter projection;
`source-pins.json` binds the checked controller/caller/protocol, existing Xiph17
reference proof and known failed baseline metadata. Source checks never call the
comparator's run/main or interpret actual PCM.

The adapter pins controller `3aa167fe...`, protocol `547655c4...`, caller
`37eaeb25...`, contract-file `6c95b8d5...`, model `847022a7...` and data-header
`b4db391f...`. Full identities are in source/pins. It requires exactly17 cases,
238 decoded packets, 398080 PCM bytes, case mask131071 and 530 protocol events.
The generic checked protocol may describe more cases, but this adapter cannot
accept a partial subset or a25-case extension.

Every input snapshot is rehashed, all nine actual owned commands and separate
direct-tool terminal/report SHA are checked, and the exact frozen pure protocol
recovers the emitted PCM. Each persisted file must match those recovered bytes,
size, hash, named case order and all14 packet offsets including zero primer.
Only frozen source paths are relocated; the full source model remains identical.
Caller and materialized data-header bytes receive explicit independent checks.

Each case is compared against the actual independently qualified Xiph17 WAV,
whose full rate/stereo/S16/frame count, PCM/WAV hashes, framemd5 packet durations,
PTS, sizes and MD5 are rechecked. Every original zero-lag L/R sample contributes
to whole-case/per-channel/per-packet signed errors, peaks, exact sums, RMS and
histogram. No trimming, gain fit, shift, swap, resampling or lag repair occurs.
Alternative lag/channel scores remain diagnostics only. Legacy core counters
named `*_clipped_samples` count S16 endpoints; they do not prove clipping cause
or incorrect scaling.

Per-channel nonzero evidence is required for every SS/SL/LS/LL transition. All
same/different relations declared in the actual two frozen source matrices must
match the independent reference proof, then all four are recomputed separately
for Xiph and checked PCM. The existing seven FFmpeg-native crosschecks, ten
lookup2 refusals and original dual NONPASS are preserved. They are distinct from
the unavailable SDK-vendor comparison: `vendor_comparison_available` and
`vendor_checked_pcm_equal` stay false.

Default `policy=null` produces measured evidence only. The optional explicit
`--max-abs-error 2` applies the predeclared project gate
`bounded-corpus-regression-not-standard-conformance`; only value2 is accepted.
It may set `bounded_corpus_pcm_qualified` after all17 cases, counts/nonzero and
relations hold. Gate failure exits1 with measurements retained; unset policy
exits0 as `MEASURED_POLICY_UNSET`. Numeric standards, format conformance, fullG6,
production and physical flags remain false, as does generic `passed`.

## Root-owned invocation after a reviewed complete capture

Do not use the failed baseline02 as a measurement input. After a compatible
complete capture is independently reviewed, the explicit interface is:

```powershell
python -B .build/cyd-vorbis-format-checked-numeric-prep-01/compare_capture.py `
  --repository . `
  --host .build/cyd-vorbis-format-corpus-host-01 `
  --qualification .build/cyd-vorbis-format-corpus-qualified-01/qualification.json `
  --host-terminal .build/cyd-vorbis-format-corpus-host-01-command.json `
  --target <reviewed-complete-checked17-capture> `
  --target-terminal <actual-direct-tool-terminal.json> `
  --target-report-sha256 <independently-reviewed-report-sha256> `
  --output .build/cyd-vorbis-format-checked-numeric-measurement-01 `
  --max-abs-error 2
```

Output must be fresh and independent beneath this repository's `.build`.
Source/process/metadata/count failures retain a partial error report and exit
nonzero; interruption exits130. No incomplete result qualifies. There is no
SDK/compiler/decoder/reference/QEMU/Git/device/network execution. This numeric
adapter does not replace SDK/binary qualification or rehash installed binaries.
