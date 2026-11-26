# CYD OpenETH TLS/HE-AAC: three-output Close regression

Socket teardown with unread TCP input can discard a queued WebSocket Close.
This campaign checks the graceful-close change with complete TLS/HE-AAC audio
and post-EOF WebUI on all three CYD audio outputs.

Source `95672e8f673ec977b6f61b78eeba6958d0d992ac` adds the negative-descriptor guards to the earlier
Close implementation `d2601b96637d50b6ec45c0e0a74ab56be99d9d57`. Graceful closure sends the Close/TLS
alert before half-closing TCP, drains at most 4,096 trailing bytes for 200 ms
with 128-byte stack scratch and no explicit local heap allocation, then
completes socket shutdown. The 200-ms/4,096-byte bounds apply only to RX
discard; lwIP FIN allocation retains the existing stack's waiting behavior.
HTTPD keeps final close/context ownership. Failed TLS sessions retain immediate
abort; prepare_close performs no socket cleanup. The source entries are the
[shared transport](../../../idf/components/native_web_transport/native_web_transport.c),
[CYD caller](../../../idf/esp32-cyd2usb-native/main/websocket_service.c) and
[C3 caller](../../../idf/esp32c3-oled-native/main/websocket_service.c).

All three final ordinary RTC-off diagnostic profiles pass the unchanged strict
controller and QEMU model used for [source 799f6787](../cyd-ws-streaming-20261126/README.md).

| Output | Measured minimum heap, bytes | Final allocation failures | PCM-flush pbuf prefix | Full gate |
| --- | ---: | ---: | ---: | --- |
| legacy | 3260 | 0 | 0 | PASS |
| pdm | 4104 | 0 | 0 | PASS |
| continuous | 3548 | 0 | 0 | PASS |

Each run consumes the complete 102,420-byte TLS/HE-AAC response with full-size
TLS 1.2 records, flushes exactly 614,400 stereo PCM16 frames at 48 kHz, and
matches PCM SHA-256 `44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`. The exact WebUI asset works during playback and
after EOF. Both WS clients receive idle/playing/EOF statuses and application
pongs, close normally with code 1000, and stop their readers. Final health is
read after the asset/status requests and peer closure; cumulative allocation
failures remain zero. The independent zero pbuf snapshot covers the PCM-flush
prefix, while later global counters cover the final peer-close phase.

PDM completion-notification queue drops are 0 at EOF and
121 after the final peer closures. This counter measures notification
queue events, not lost PCM frames. Exact PCM, requested/written byte equality
and the separate zero driver error/timeout/short-write gates remain recorded.

The [summary](summary.json), [manifest](MANIFEST.json), per-output
[native reports](native/continuous/report.json), [input receipts](native/continuous/input-verification.json)
and [SDK qualifications](sdk/continuous/qualification.json) bind the actual
source, app, ELF, config, controller/model and exact linked pbuf proof.
Controller SHA-256 is `ca236ed51cbb54e06391e7cfb5b88ef465594ccfbd122e52ddcade64f479cc4f`; QEMU SHA-256 is `28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4`. TCP/TLS,
audio/core/task/watchdog budgets and the earlier streaming-status policy remain
unchanged. Static section/heap-start deltas relative to 799f6787 are zero.

Host ASan/UBSan results are CYD 82 groups in each DRAM/RTC mode, C3 IO 5,191
cases with four historical controls, shared transport 86 groups (69 original
plus 17 close/descriptor groups) with five defective controls, and 164 integrated
localhost TCP cases on each of CYD/C3. Three complete GCC images and matched
before/after whole-unit Clang checks of the two affected CYD consumers include
system headers; selected pbuf.c/tcp_out.c SDK frontends and the ELF/link proof
also pass. Final warning catalogs match the prior qualified source. These
focused checks do not claim a new full-project compiler audit, complete
worst-case stack depth, physical RAM margin or physical timing qualification.

The [earlier d260 SDK warning attempt](history/d260-warning-attempt/qualification.json)
remains NONPASS. The later fd guards do not rewrite that outcome or claim an
earlier guest run. The retained [real TLS](history/d260-tls/cyd/report.json)
and [combined WSS](history/d260-wss/report.json) reports use d260 transport
source: real loopback TLS/crypto with the stated host HTTPD/NVS/SDK/type seams.
They do not qualify the final 956 source on the actual target. Full independent
actual-target WS/WSS RFC qualification remains pending; this resource run uses
TLS audio, HTTP WebUI and ordinary WS. Whole-service Stop/join remains separate.

The audio fixture's unchanged [certificate-date policy](../cyd-pbuf-failure-probe-20261124/native/root-records/tls-date-policy-20261126.json)
does not validate expired fixture certificate dates. This is separate from the
fresh host-verified identity for a future WSS gate. No physical board is
connected. Remaining delivery is fresh-source WS/WSS qualification, twelve CYD
production exports (six ordinary and six RTC), current C3 compiler/artifact
refresh, and conditional board acceptance. Extended private Vorbis, compact/
private AAC ABI/reset/owner-view, and FLAC target OOM/backpressure/semantic
controls stay explicitly deferred. No binaries, credentials, NVS or composed
flash are included; old raw outcomes remain unchanged.
