# ESP8266 HTTP receive throughput, 2026-09-08

## Result

In the original timing profile, the best 20-second receive-only average was **569.9 kbit/s**
(71.24 kB/s). Two further complete unpaced runs gave **460.5 and
523.7 kbit/s**. This is useful HTTP body throughput in the current
firmware/network, not the chip's maximum Wi-Fi PHY rate. The largest
one-second bin was **1.056 Mbit/s**; it is a burst, not sustainable speed.

Do not treat 460 kbit/s as a guaranteed floor: the fourth unpaced attempt
received only 408 bytes and ended on the configured 1-second inactivity
timeout. That failure is retained, not discarded as an outlier.

Paced receive-only tests kept up with 64/128/320-kbit/s sources on average.
They were bursty: the 320-kbit/s test had a **947-ms gap between successful
reads**. With decoding and PDM/DMA output enabled, useful input throughput
fell below the source rate in all three tested cases. Average network
capacity alone therefore does not establish continuous radio playback.

## Conditions and method

- Physical Wemos D1 mini / ESP8266EX, CPU 160 MHz, QIO 40 MHz.
- Native RTOS firmware, existing HTTP client/audio task, Helix MP3 SSO and
  AAC-LC, mono. I2S PDM32 on GPIO3/RX, 2 x 512 DMA words, nominal
  1.536 MHz / actual 1.538461 MHz carrier. No PC Wi-Fi settings changed.
- Board 192.168.100.6; source PC 192.168.100.253:8765 through Ethernet and
  the same router. According to the user's earlier description, roughly
  6 metres, one wall and a wooden door. RSSI sampled at case boundaries
  ranged from -84 to -71 dBm; these are not continuous min/max readings.
- Local unencrypted HTTP/TCP excludes the Internet and radio-station
  server as bottlenecks. It does not exclude the router, TCP stack,
  scheduling, interference, or Wi-Fi. No TLS or UDP tested.
- Own repeatable tone/noise MP3/AAC fixtures, same as the flash benchmarks.
  The server loops complete encoded files, advertises Content-Length and
  Connection: close, and honors socket backpressure. Unpaced responses
  advertise at least 128 MiB without allocating that much RAM. Paced
  responses offer 35 seconds of data; the board measures about 20 seconds.
- No whole-file copy on the board. Reads are capped at 1024 bytes into the
  existing 1536-byte decoder input allocation. The native successful-read
  and EAGAIN yields remain 1 ms. Inactivity timeout remains 1000 ms.
- TCP MSS 536, receive window 2440, receive mailbox 6; SO_RCVBUF disabled.
  These are existing settings, not tuned for this benchmark.
- Receive-only retains the same decoder allocation as playback: MP3
  DRAM 8440 + IRAM 16384 bytes, or AAC DRAM 6804 + IRAM 16384 bytes.
  Received body bytes are discarded after counting in receive-only mode.
  Wi-Fi, HTTP/WebSocket services and neutral DMA remain enabled, but no
  browser-load stress is generated during the measured windows.
- Playback uses the real decoder and native PCM-to-PDM/DMA callback.
  Normalization is disabled and runtime volume is 128, balance zero;
  the benchmark does not explicitly commit these overrides to NVS. Smart-start is disabled
  only in the diagnostic image. No extra producer task or buffer added.
- UART prints occur after each window, not periodically inside it.
  Measure elapsed wall time, not CPU utilization. Count body bytes on
  the board, not bytes merely accepted into the PC's TCP send buffer.
  HTTP connection/header time is measured separately and excluded.

## Unpaced receive-only maximum attempts

| Capture / case | Measured time | Received body | Average kbit/s | Largest read gap | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| matrix / 0 | 20.000386 s | 1,424,732 B | 569.882 | 328.331 ms | complete |
| bulk / 0 | 20.000378 s | 1,151,244 B | 460.489 | 921.355 ms | complete |
| bulk / 1 | 20.001277 s | 1,309,360 B | 523.711 | 523.960 ms | complete |
| bulk / 2 | 1.000207 s | 408 B | 3.263 | 1000.216 ms | timeout, error -116 |

The first three completed windows span 60 seconds in total, with gaps
between cases; they are not one continuous minute of successful transfer.
The partial fourth run must not be averaged over an invented 20 seconds.
Its log still prints all 20 bucket slots; slots beyond the measured time
are unused zeros, not observations. No statistical long-term guarantee
can be inferred from four attempts.

Additional CPU-profile runs below reached **816.5 kbit/s** (102.07 kB/s)
and **518.8 kbit/s**, each for about 20 seconds. The overall largest
one-second bucket was **1.400 Mbit/s** in the CPU profile. Thus the largest
observed 20-second rate across all profiles is 816.5, not 569.9 kbit/s;
the latter belongs to the original timing profile only. Runtime tracing
changes memory/timing slightly and RSSI varied, so this is not evidence
that instrumentation or a code optimization increased throughput.

## Paced input versus active audio output

All rows below ran for approximately 20 seconds and ended without a
transport/decode error. That does **not** mean playback kept up.

| Source | Receive only, kbit/s | Decode + PDM, received kbit/s | PCM produced in ~20 s | Playback underruns |
| --- | ---: | ---: | ---: | ---: |
| MP3 128 kbit/s | 128.283 | 54.019 | 8.438 s | 8652 |
| MP3 320 kbit/s | 320.508 | 126.638 | 7.889 s | 9069 |
| AAC-LC 64 kbit/s | 64.300 | 52.186 | 16.533 s | 2665 |

AAC is offered at exactly 64 kbit/s including framing; its file's actual
encoded average is about 63.126 kbit/s, so source byte pacing is slightly
faster than the clip's natural audio duration. Loop/encoder boundaries
are another reason not to extrapolate this short fixture to every station.
They do not account for the large MP3 receive-rate deficit.

Underruns count neutral-output retries, not lost MP3/AAC frames or separate
audible dropouts. Receive-only deliberately produces no audio; its neutral
DMA counters must not be interpreted as playback failures. No analog
capture, listening certification, PCM equivalence or SNR measured here.

## Where time is lost

| Mode / source | Max gap between successful reads | Max interval outside receive | Longest EAGAIN episode | Max decode/PCM commit |
| --- | ---: | ---: | ---: | ---: |
| receive MP3 128 | 434.204 ms | 3.770 ms | 433.346 ms | none |
| receive MP3 320 | 947.421 ms | 4.025 ms | 946.264 ms | none |
| receive AAC 64 | 573.032 ms | 3.804 ms | 571.836 ms | none |
| play MP3 128 | 831.747 ms | 82.050 ms | 806.773 ms | 80.937 ms |
| play MP3 320 | 333.385 ms | 40.649 ms | 299.379 ms | 40.205 ms |
| play AAC 64 | 234.323 ms | 186.687 ms | 152.650 ms | 186.107 ms |

The receive-only task returned to polling within a few milliseconds,
yet no data was available to the application for hundreds of milliseconds.
These pauses are not explained by MP3 decoding: there was no decoding
in those cases. Weak/variable reception is plausible, but these counters
alone do not prove RF loss versus TCP window/ACK behavior or scheduling.

During playback the decoder commit includes PCM conversion, synchronous
DMA waits and preemption. Its maximum is **not pure decoder CPU time**.
It also delays the next read because receive/decode/output share the
audio task. EAGAIN episode durations include yields and time between
probes; they are not a continuously observed hardware socket-empty state.

FIONREAD probes are unsupported in this lwIP configuration. JSON reports
therefore use ready_max=null / ready_probe_supported=false. The raw
ready_max=0 must not be cited as proof that the receive queue was empty.

Free heap minima: 11,692..14,052 bytes for complete receive-only cases,
11,048..13,028 during playback. Audio task stack high-water margin:
1264..1272 bytes. These are free-memory measurements with decoder memory
retained, not memory consumed by the benchmark or whole-system idle time.

## Implications and next work

The prioritized implementation checklist is saved separately in
[the Wi-Fi/HTTP receive optimization plan](ESP8266_WIFI_RX_OPTIMIZATION_PLAN.md).
Saving the plan does not enable its production changes.

1. Current HTTP reception has average headroom over 320 kbit/s, but no
   tested bitrate is certified continuously reliable in these conditions.
2. At 320 kbit/s, bridging the observed 947-ms receive-only gap would need
   roughly 37.9 kB of compressed prebuffering alone (before a safety
   margin). The existing 1536-byte codec input spans only 38.4 ms at that
   bitrate, and reported free heap cannot supply 38 kB. Simply enlarging
   that buffer is not presently a safe complete solution.
3. To isolate RF from TCP behavior, compare unchanged firmware at better
   reception and capture sender-side TCP ACK/window/retransmission timing.
   No RSSI-only conclusion or TCP-setting change is justified by this run.
4. Separately trace PCM/DMA deadlines. The previous flash benchmarks
   already found MP3-320 and AAC output gaps with Wi-Fi disabled. Network
   buffering alone cannot repair that independent output-path problem.
5. Production decoder/output behavior was not changed by this diagnostic.
   The WebUI latency/continuous-audio acceptance goals remain unresolved.

## Receive-only CPU time: follow-up measurement

Enable native FreeRTOS runtime counters using the 1-MHz ESP timer, not the
32-bit CPU-cycle clock which wraps too quickly. Snapshot task counters
before/after each window. Subtract snapshots and divide task runtime by
the counter's elapsed interval. Connected baseline: 20 seconds without a
stream, with the MP3 allocation retained and neutral DMA/WebUI enabled.
The baseline shows about **2.17% non-idle / 97.83% idle**.

The first CPU profile kept the detailed per-poll probes. At 816.5 kbit/s
it measured 60.63% non-idle: reader 22.89%, tiT 20.66%, ppT 16.15%.
Its paced 128/320/64 cases timed out after 2.879/7.307/1.912 seconds;
they are retained in cpu.json, not represented as completed windows.

For a cleaner estimate a second CPU image removes unsupported FIONREAD,
repeated gap timestamps and per-poll heap queries. It retains only two
timestamps around stream_receive(), byte/call counting and per-second
buckets, plus task snapshots outside the inner loop. The production
1024-byte read limit and 1-ms yields remain. No decoding or PCM modulation
occurs in this receive-only test; neutral DMA keeps running.

| Offered rate | Actual receive rate | Reader task | TCP/IP tiT | SDK network ppT | All non-idle | Idle | Measurement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 64 kbit/s | 64.23 kbit/s | 16.14% | 2.76% | 2.66% | 22.27% | 77.73% | 20.02 s complete |
| 128 kbit/s | 128.14 kbit/s | 16.25% | 4.53% | 3.92% | 25.39% | 74.61% | 20.02 s complete |
| 320 kbit/s | 302.24 kbit/s | 16.68% | 9.65% | 7.64% | 34.67% | 65.33% | timeout after 17.38 s |
| unlimited | 518.77 kbit/s | 16.72% | 14.12% | 10.99% | 42.55% | 57.45% | 20.03 s complete |

At 64/128/519 kbit/s, the reader plus tiT/ppT consume about
**21.57/24.69/41.84%**. Other non-idle tasks account for roughly another
0.7 percentage points. Relative to the 2.17% connected baseline, total
additional non-idle load is approximately **20.10/23.22/40.38 percentage
points**. These background-subtracted values are estimates, not isolated
hardware Wi-Fi IRQ costs.

The reader's roughly 16% is largely independent of bitrate. At 128 kbit/s,
18,793 read attempts over 20.02 seconds included **18,200 EAGAIN returns**;
at 64 kbit/s, **19,045 of 19,339** returned EAGAIN. The 1-ms poll repeatedly
enters the socket stack even when no bytes can be read. Waiting for socket
readiness is a concrete next optimization candidate. It has not been
implemented in production by this task.

Do not sum elapsed recv time with TCP/IP task time: a recv call can be
preempted, including by the TCP/IP task, so these wall-time spans overlap.
For example the unlimited lean run accumulated 4.852 seconds inside
receive calls, but the reader task itself was charged only 3.354 seconds
of runtime. TCP waiting while the task sleeps is not counted as reader
runtime. These measurements are not end-to-end HTTP request latency.

Accounting limitations: FreeRTOS charges interrupts to the interrupted
task, so IDLE residency is not a separately instrumented hardware sleep
counter and IRQ CPU cost cannot be fully isolated. Task-boundary snapshot
skew is about a few tens of milliseconds per 20-second window. The CPU
profile adds 1440 bytes of static snapshot storage and task-counter
overhead; it is not zero-cost instrumentation. SDK configuration differs
from the original timing profile only by the runtime-stat options. The
64/128/320 CPU cases are receive-only, not decoder-specific CPU results.

Lean reports intentionally set unmeasured gap metrics to null, not zero.
Heap is only sampled: heap_final on success or heap_initial on an early
error, never presented as a measured minimum. RSSI in the lean case
endpoints ranged from -85 to -67 dBm. The 320 timeout is not discarded.
All raw task counters and failure cases are retained in
[cpu.json](benchmarks/esp8266-network-2026-09-08/cpu.json) /
[cpu.log](benchmarks/esp8266-network-2026-09-08/cpu.log) and
[cpu-lean.json](benchmarks/esp8266-network-2026-09-08/cpu-lean.json) /
[cpu-lean.log](benchmarks/esp8266-network-2026-09-08/cpu-lean.log).

Deployment note: several OTA transfers were rejected after incomplete
reception (HTTP 400 and image validation finding unwritten flash). The
running slot was retained; a successful retry was needed. One passive
transition capture also contains a stack-canary diagnostic before the
CPU-profile application successfully started. Its cause was not diagnosed
by these measurements; no canary/reset was logged inside the measured
windows. Do not interpret this benchmark as OTA/reboot reliability approval.

## Reproduction and saved evidence

- Firmware switch YORADIO_ESP8266_NETWORK_BENCHMARK=ON; server URL via
  YORADIO_ESP8266_NETWORK_BENCHMARK_URL=http://192.168.100.253:8765.
  Set YORADIO_ESP8266_NETWORK_BENCHMARK_BULK_ONLY=OFF for the 7-case matrix
  or ON for three unpaced receive-only repetitions. Other benchmark,
  audio-profile and codec-RAM options must be OFF; AAC enabled.
- For CPU tests, append tools/esp8266_audio_profile/network_cpu.defaults
  to a copy of canonical sdkconfig.defaults and pass that combined file
  as SDKCONFIG_DEFAULTS to a fresh build. This SDK accepts one defaults
  filename, not a semicolon-separated list. Set NETWORK_BENCHMARK_CPU_ONLY
  (with the same YORADIO_ESP8266_ prefix) ON, BULK_ONLY OFF.
  This selects a connected baseline and four receive-only cases. Restore
  normal production after testing; do not enable tracing there by default.
- Start `node tools/esp8266_audio_profile/network_source.cjs` on the LAN
  PC; its bind address is explicit. Capture TX UART passively with
  `tools/monitor_esp8266.py` (no --reset, no UART commands).
- Convert the log using
  `node tools/esp8266_audio_profile/summarize_network.cjs capture.log report.json`.
  A partial/failing case yields a nonzero exit status while still saving
  all results. Summary complete=true means the test loop ended, not that
  every case passed. kept_up describes average byte rate, not continuity.
- [Matrix JSON](benchmarks/esp8266-network-2026-09-08/matrix.json) and
  [UART](benchmarks/esp8266-network-2026-09-08/matrix.log).
- [Unpaced repeat JSON](benchmarks/esp8266-network-2026-09-08/bulk.json) and
  [UART](benchmarks/esp8266-network-2026-09-08/bulk.log), including timeout.
- [Build/config hashes](benchmarks/esp8266-network-2026-09-08/builds.json).
- [MP3 flash comparison](ESP8266_MP3_FLASH_BENCHMARK_2026-09-08.md) and
  [AAC flash comparison](ESP8266_AAC_FLASH_BENCHMARK_2026-09-08.md).

Diagnostic app binaries and sdkconfig are retained under
firmware/development/esp8266-network-profile/ and esp8266-network-bulk/.
The production builder explicitly disables all network benchmark modes
and clears the test URL. Use the ordinary I2S PDM production image after
testing; a network benchmark image is not the normal radio.

## Final board state

The ordinary production app was restored by OTA after the CPU tests:
HTTP 200 / OK, then running slot changed from 0x110000 to 0x10000.
Wi-Fi connected, native status reports no error, and HTTP GET / returned
200 with 27,162 bytes in 223 ms. This is one response measurement, not a
browser full-page/control-latency acceptance test. Radio was left stopped.
The temporary LAN server was stopped and passive serial monitors ended.
No SPIFFS/NVS partition was erased or reflashed, and PC Wi-Fi settings
were not changed. Normal OTA stop handling may persist the stopped
playback state through the application's usual settings mechanism.
See [deployment verification](benchmarks/esp8266-network-2026-09-08/deployment-verification.json).
