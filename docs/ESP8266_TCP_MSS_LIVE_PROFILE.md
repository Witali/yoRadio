# Full TCP MSS: diagnostic live-radio profile

2026-09-17. `build_i2s_pdm_production.ps1 -Diagnostic -TcpFullMss`:

| Setting | Unchanged default | Experiment |
|---|---:|---:|
| TCP MSS |536|1460|
| Send-buffer limit |2440|2920|
| Receive window |2440|2920|

The pinned Espressif SDK exposes these settings in `components/lwip/Kconfig`.
Its ESP8266 Wi-Fi netif uses MTU1500. Send and receive limits here both hold
two full segments. No MTU, Wi-Fi adapter, TCP semantics or decoder arithmetic
is changed. The RX window grows480B; actual dynamic memory also depends on
packet count, pbuf headers, out-of-order data, and concurrent WebUI traffic.
This is not a claim of zero RAM cost or proven throughput improvement.

Rationale: test whether fewer packet/ACK/stack transactions improve live
Opus24 while retaining the4096B free-DRAM guard. A current RX-diagnostic
control showed no custom-allocation/enqueue/immediate-TX failures during
a faulty steady playback window. These counters do NOT count every RF loss
or Wi-Fi TX completion/retry, and do not exonerate the entire network path.

The option is diagnostic-only. Cache guards reject mismatched or duplicate
MSS/window settings. The manifest records actual requested profile fields.
Three profile tests PASS. Keep the original defaults until physical trials
show repeatable continuous PCM/DMA output and adequate memory. Ten attempts
must retain all failures; do not infer audio continuity from Playing alone.
