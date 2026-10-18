# CYD portable HTTP/ICY/probe transfer

Software regression evidence for CYD-C3-02. Host tests compile production
helpers/tasks and actual SDK HTTP/ESP-TLS read functions under ASan/UBSan.
Codecs, transport, scheduling and device I/O are scripted where required.
TLS cryptography, physical DMA, sound and network acceptance remain pending.

| Coverage | Evidence |
| --- | --- |
| Actual CYD stream task, HTTP startup/status/deadline, redirects, retry/fatal TLS, allocation failure, cancellation, ICY and JSON status: 42 scenarios | [CYD task](cyd-stream/report.json), [log](cyd-stream/test.log) |
| ICY every split and 1/7/2048-byte reads, maximum/zero metadata, title clear/truncation, exact audio replay, backpressure and interval bounds | [Shared parser](native-stream-body/report.json), [log](native-stream-body/test.log) |
| Bounded JSON at every capacity, control bytes, Unicode, malformed/truncated UTF-8 and 1,000 deterministic inputs validated by Python JSON | [Shared parser](native-stream-body/report.json) |
| Fragmented codec probe, ID3, unknown input and byte-exact replay across 11 media fixtures, six cases each, both targets | [CYD corpus](cyd-stream-probe/results.json), [C3 corpus](c3-stream-probe/results.json) |
| Actual HTTP parser/read/body/completion functions and ESP-TLS adapter from IDF 6.0.2 and pinned C3 IDF 6.1: 93 cases per target | [CYD SDK](cyd-http-reader/report.json), [C3 SDK](c3-http-reader-shared/report.json) |
| Existing TLS profiling wrapper after common EOF-result extraction | [C3 profiling](shared-stream-tls-profile/report.json) |
| Lifecycle, ordered completion, OOM, stale callbacks/titles and 2,000 concurrent Play/Stop commands in each codec-service branch | [Lifecycle](cyd-lifecycle/report.json) |

The SDK-reader tests retain a negative control showing that the unmodified
ESP-TLS adapter collapses `close_notify` and raw transport EOF. The source-scoped
adapter preserves that distinction, without changing explicit HTTP framing or
allocating another TLS buffer. Its mbedTLS results are scripted, not encrypted
network traffic. Adjacent-frame confirmation and format-transition routing
remain the following plan stage.

Complete clang-tidy reports are retained in the
[static-analysis campaign](../native-lint-20261018/). Full analysis with warnings
does not mean every diagnostic has been resolved. Firmware manifests are saved
separately after production GCC builds; no image from this campaign has been
installed on a board.
