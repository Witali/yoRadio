# CYD streamed status: full OpenETH TLS/HE-AAC qualification

Source `799f6787b152ef588b6f0c6c77195eca2eb4bdf0` replaces the persistent
5,120-byte rendered WebSocket status with a 1,024-byte HTTPD-owned staging
buffer and a four-byte cached length. Logical capacity remains 5,120 bytes,
with the same fields/order/escaping, two clients and one absolute one-second
budget for each complete frame. Header and payload are coalesced into one
unmasked FIN/TEXT frame, even when its bytes need several transport writes.
No TCP/TLS, channel, audio/task/core or OpenETH RX policy is changed.

All three ordinary RTC-off diagnostic profiles pass the unchanged strict
controller with the corrected OpenETH exact-length RX and self-clearing I2S
START QEMU model. The independent pbuf observer remains enabled in each app.

| Output | Static heap-start recovery, bytes | Runtime minimum heap, bytes | Final allocation failures | Full gate |
| --- | ---: | ---: | ---: | --- |
| legacy | 4080 | 3716 | 0 | PASS |
| pdm | 4096 | 3908 | 0 | PASS |
| continuous | 4096 | 6064 | 0 | PASS |

Each run consumes the full 102,420-byte HE-AAC stream over TLS with full-size
records and flushes exactly 614,400 stereo PCM16 frames at 48 kHz. PCM SHA-256
is `44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`.
WebUI works during playback and after EOF. Both WebSocket clients receive
idle/playing/EOF statuses, answer commands and close normally. The final
status/health check occurs after the last asset request and peer closures;
global allocation failures remain zero. The independent PCM-flush pbuf
snapshot is present and zero for all outputs; it is a prefix observation,
while the later global fault count covers the final phase.

## Evidence and limits

The [summary](summary.json), exact [file manifest](MANIFEST.json), per-output
SDK reports and native reports/UART retain the actual source/config/image/ELF,
controller/model and prior qualification bindings. Diagnostic images, object
archives, TLS material, NVS and composed flash remain local. Static recovery
includes the actual four-byte count and linker alignment; it is not inferred
only from the array-size difference. Individual Xtensa frames are measured;
complete worst-case stack depth and physical timing are not established.

The [host evidence](host/MANIFEST.json) retains both 79-group ASan/UBSan modes,
81,501 exact-original JSON differential cases and four defective encoders,
the real source deadline-regression rejection, and seven C3/CYD downstream
suites. The extreme 4,899-byte status is byte-identical to the original f7
formatter. Shared state is immutable between counting and emission; arbitrary
cache corruption is outside this ownership invariant. Host transport seams
do not replace independent actual-target WS/WSS conformance qualification.
The [integrated TCP suite](host/protocol/report.json) also passes 164 cases
on each of CYD and C3. Its initial CYD compile failure is retained: the fixture
needed the existing scheduler's declarations; application code was unchanged.

PDM's completion-notification queue counter is 0 at EOF and 117
after final peer closure. It is separate from PCM loss; requested driver bytes
equal written bytes, with zero driver errors/timeouts/short writes. The exact
PCM observation does not establish physical audio quality.

Initial local qualification failures (SDK tool sandbox and baseline line-ending
precheck) remain recorded separately; their corrected checks do not rebuild or
reclassify failed native runs. Earlier
[RTC-off failures](../cyd-openeth-no-rtc-20261124/README.md) and
[pbuf attribution](../cyd-pbuf-failure-probe-20261124/README.md) stay unchanged.
The retained certificate-date policy is
[documented separately](../cyd-pbuf-failure-probe-20261124/native/root-records/tls-date-policy-20261126.json):
this workload does not qualify certificate date validation. No physical board
was connected, and this result does not retrospectively prove the cause of
the earlier intermittent continuous-DAC timeout.
