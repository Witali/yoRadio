# CYD health pipeline and HTTP integration

Software regressions compile actual production functions under ASan/UBSan:

- [Health core/JSON](core/report.json): quiet and diagnostic32/64 fault snapshots,
  60,000 concurrent events per category, output error categories, CPU lifetime /
  wrap / two-core denominator, and every JSON buffer capacity at integer maxima.
- [Pipeline](lifecycle/report.json): six queue/codec branches; decoder faults
  retain stage/vendor result before cleanup, stale cancellation is ignored,
  normal EOF/drain does not add failures, and configuration/write/final-flush
  errors remain distinct. Input health removes packet headers and guards
  subtraction, absent pools and the ring fallback.
- [HTTP](http/report.json): actual health handler and JSON formatter with SDK
  heap/task seams, correct capability views, immutable counters and state,
  no-store headers, and HTTP 500 on formatter failure. Existing 42 HTTP/ICY
  scenarios and status Unicode/bounds checks continue to pass.

The endpoint uses a 2,304-byte response buffer verified at maximum field values.
Internal and DMA capabilities overlap. Stack absence and uncollected CPU values
are `null`; retained encoded bytes are not a playback-duration guarantee.

Both ESP-IDF 6.0.2/GCC 15.2 profiles built from clean `b7362172`:

| Profile | Saved image | Bytes |
| --- | --- | --- |
| Quiet PDM | [manifest](../../../firmware/development/esp32-cyd2usb-native-health-pdm/manifest.json) | 1,369,920 |
| Diagnostic PDM | [manifest](../../../firmware/development/esp32-cyd2usb-native-health-diagnostic-pdm/manifest.json) | 1,373,328 |

Quiet preserves every existing baseline sdkconfig value. Diagnostic changes
runtime stats/trace and uses the global ESP timer; the manifest enumerates the
differences. Both keep prefill at zero and fit the 0x1b0000 application slot.
ELF symbols place the failure callback in `.iram0.text` and its lock/snapshot
in `.dram0.data`; [symbol evidence](iram-symbols.txt).

Full clang-tidy/Clang Static Analyzer runs complete all 16 own translation units:
[quiet](../native-lint-20261018/cyd-health-quiet/report.json) has 11 warnings,
[diagnostic](../native-lint-20261018/cyd-health-diagnostic/report.json) has 13,
both zero errors. The extra pair requests explicit pointer conversion for
`memcpy` of a fixed pointer array; it is not a buffer/lifetime finding.

Transport, codec and driver APIs are seams in pipeline tests; the fault/sampler
core uses actual host mutexes. ISR latency, DMA and physical CPU/headroom remain
separate acceptance work. C3 single-core IRQ masking was not copied to CYD.
