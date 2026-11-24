# CYD RTC SLOW WebSocket memory qualification

An optional placement change frees 6,560 bytes of ordinary DRAM without
reducing WebSocket capacity, channel count, TCP windows or TLS records.
PDM and continuous DAC complete full TLS/HE-AAC playback with two live
WebSocket clients in the latest QEMU runs. Legacy DAC completes the same
audio and WebUI work but records one recovered allocation failure, so its
resource result remains **NONPASS**. The option stays experimental and off
by default; this checkpoint does not close the overall memory-margin gate.

## Current two-client runs

All use the full 102,420-byte HE-AAC fixture, normal TCP RX 11,520 / mailbox
10 / TX 5,760, TLS capacities 16,384/4,096, static TLS buffer policy without
the separate static-RX loan, five-second task watchdog and 300 ms interrupt
watchdog. The original two-core audio task bindings are unchanged.

| Placement / output | Result | PCM frames at ordered flush | Allocation failures | Minimum free heap |
| --- | --- | ---: | ---: | ---: |
| DRAM control / PDM | NONPASS: WebUI connection closed | No complete flush | No EOF sample | No EOF sample |
| RTC workspace / PDM | PASS | 614,400 | 0 | 324 B |
| RTC workspace / continuous DAC | PASS | 614,400 | 0 | 1,744 B |
| RTC workspace / legacy DAC | NONPASS | 614,400 | 1 | 1,412 B |

The three complete outputs have the original full PCM SHA-256
`44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`.
Each receives the complete TLS response and exact 13,588-byte WebUI asset
after EOF. Both continuously drained clients observe idle, playing and EOF
with increasing receipt numbers, receive three application pong replies,
and close normally with code 1000. The legacy run has one 1,522-byte
allocation failure and a matching recovered OpenETH RX wait; complete PCM
does not override the zero-failure resource criterion. The PDM control also
has abnormal client closes and is not presented as a passing client test.

The 324-byte PDM minimum is a very small observed margin, not a guarantee
for different traffic, longer sessions or worst-case status text. These
finite emulator results do not justify enabling the option by default.

## Earlier controls retained

The [observations](observed.json) retain 11 original terminal reports and
raw UART logs, including the four latest runs above and these earlier runs:

| Earlier case | Result | Detail |
| --- | --- | --- |
| DRAM PDM, no live peers | NONPASS | Incomplete 1,024-byte WebUI read |
| RTC status buffers, PDM, no peers | PASS | 0 allocation failures, 3,704 B minimum |
| RTC status buffers, continuous, no peers | PASS | 0 failures, 6,732 B minimum |
| RTC status buffers, legacy, no peers | PASS | 0 failures, 1,784 B minimum |
| RTC status buffers, PDM, first two-peer probe | NONPASS | No idle WebSocket status |
| RTC status buffers, PDM, corrected Ethernet status adapter | NONPASS | Full PCM and peers, 4 allocation failures |
| RTC full workspace, PDM, initial command probe | PASS | Full PCM, 0 failures, 1,800 B minimum |

The first live-peer probe exposed a test-backend defect: it queried the
absent production Wi-Fi runtime, so status capture never succeeded. The
OpenETH-only snapshot wrapper now reports the actual Ethernet interface;
Wi-Fi profile and valid RSSI remain absent. This is not a production Wi-Fi
change or a successful memory test reclassified from that initial failure.

The first placement moved only JSON and two snapshots (6,136 object bytes).
The current workspace additionally moves fixed client state and the socket
list (6,560 total). The diagnostic workload evolved to include application
commands and then strictly newer phase receipts. Earlier runs retain their
own source/helper hashes and original outcomes; they are not all matched
runtime comparisons of a single variable.

## Placement and other checks

The saved ELF identities show all five current workspace objects in
`.rtc.force_slow`, inside classic ESP32's shared RTC SLOW range. In the
matched latest PDM pair, the only effective configuration difference is
`YORADIO_WS_STATUS_RTC_SLOW`; BSS and heap-start placement each improve by
exactly 6,560 bytes. Diagnostic RTC usage is 6,664 bytes with 1,504 bytes
remaining below the separate 24-byte reservation. These numbers include
the 64-byte diagnostic access buffer.

Every retained target run completes the byte/string probe on both cores:
256 phases over all 64 bytes, including odd-offset copies, overlapping
move and string operations. This establishes execution in this QEMU model,
not physical timing. Actual linked ELF/map/config identities and project
translation-unit hashes are preserved; full build artifacts and compiler
dependency closure are not published or implied.

The retained-client host negative fails without registration clearing.
The current DRAM and RTC host configurations each pass 60 groups under
ASan/UBSan, including that correction and maximum 4,899-byte status JSON.
The host RTC section attribute does not establish target access rights.
Normal-PDM Clang-Tidy completes 53 units with zero errors and exactly the
same 100 previously reviewed warnings; its report, configuration delta and
comparison are included under `qualification/`.

`earlier-source/` preserves the earlier status-only source snapshots, not
the implementation for every later run. Each report's own hashes and
identity describe its scope. `observed.json` binds the copied reports,
UART and qualification records without reinterpreting excluded binaries.
RTC access records preserve the original controller result separately
from success of the independent memory-access probe.

## Reproduction and remaining work

See [placement and isolated build instructions](../../../docs/CYD_WS_RTC_MEMORY.md)
and the [OpenETH runner](../../target/cyd_full_app_openeth_qemu/README.md).
Use an isolated normal quiet profile, add the RTC option and diagnostic
PCM/SHA-256, allocation, RX-backoff and RTC-access hooks, then run
`--codec aac --aac-profile he --through-eof --full-tls-records --websocket-clients 2`.
The optional peers use the installed `websockets` 17.0.1 client library.
Each result directory must be fresh. Disposable CA keys, complete flash,
ELF/map and raw build output remain local under ignored `.build`.

Remaining work includes the legacy two-client allocation failure, a useful
memory margin on all outputs, RTC-enabled normal production exports and
physical Wi-Fi/audio, RTC timing and sleep/wake acceptance. Existing
production images and hardware defaults are unchanged. Private AAC,
extended custom Vorbis and previously deferred FLAC target error controls
remain deferred.
