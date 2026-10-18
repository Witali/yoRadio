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

This stage has host evidence only until SDK firmware/analysis results are added.
Transport, codec and driver APIs are seams in pipeline tests; the fault/sampler
core uses actual host mutexes. ISR latency, DMA and physical CPU/headroom remain
separate acceptance work. C3 single-core IRQ masking was not copied to CYD.
