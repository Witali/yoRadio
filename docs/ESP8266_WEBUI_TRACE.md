# ESP8266 WebUI latency tracing

Optional diagnostic profile added 2026-09-08. It measures a slow load instead
of assuming every outlier is a weak Wi-Fi signal. Ordinary builds exclude
`httpd_trace.c` and compile the hooks to no-ops.

## Capture

```powershell
powershell -File tools/esp8266_audio_profile/build_spi_pdm_debug.ps1 -WebProfile
```

The separate radio image is saved in
`firmware/development/esp8266-spi-pdm-debug-web-trace/`. It keeps SPI-PDM on
GPIO13/D7, CPU160/QIO40 and the optional gzip playlist enabled. No tone test.
The script does not flash. Flash only the application at 0x10000 using the
existing board workflow; do not erase credentials/SPIFFS or change partitions.
Wait for DHCP after resetting, before timing page loads.

In separate terminals, while that image is running:

```text
.build/esp8266-python/Scripts/python.exe -X utf8 tools/monitor_esp8266.py --port COM8 --seconds 180
powershell -File tools/trace_esp8266_ping.ps1 -Seconds 180 -Output <ping.json>
node tools/test_esp8266_webui_latency.cjs --rounds 6 --controls --playback --stress --trace --netlog --output <browser-dir>
node tools/analyze_esp8266_web_trace.cjs --report <browser-dir>/results.json --serial <uart.log> --ping <ping.json> --output <analysis.json>
```

Redirect/capture the UART terminal to `<uart.log>`. Only one program may own
COM8. The monitor never sends application UART commands. `--reset` belongs
to a separate boot check, not a benchmark. Node needs the existing Playwright
runtime and installed Edge. Tests temporarily exercise real player buttons
and restore station, volume and playback state. ICMP sends only two probes
per second by default; no adapter, route or PC Wi-Fi configuration changes.

## What is measured

Responses include `X-YoRadio-Trace`, a per-boot random prefix and request
sequence. It correlates a browser resource with a board record; source and
query parameters are not used as an identifier. The board records no query,
headers, credentials, WebSocket messages or file contents. Only a bounded
path, counters, times and result are printed.

| Field | Meaning |
|---|---|
| `start_us`, `total_us` | Board uptime and wall time from HTTP processing start to handler completion |
| `parse_us` | Time until URI dispatch (not time waiting in the server's accept queue) |
| `select_wait_us` | Previous `select()` wall time; can include ordinary idle before a request existed, never automatically excluded |
| `dispatch_us` | Time from `select()` return to this session's processing start; includes earlier handlers, control work and preemption |
| `dispatch_flags` | 1: socket reported readable by `select`; 2: only HTTP's buffered data; 0: no session-dispatch context |
| `tcp_rx_us`, `tcp_rx_len`, `tcp_seq_gap` | Most recent payload seen by lwIP for this remote port: uptime, bytes, sequence minus expected; zero length means unavailable |
| `recv_us` | Wall time inside socket receives; overlaps parsing and possibly body handling |
| `read_us` | Wall time reading playlist payload blocks from SPIFFS, cached or identity |
| `send_us`, `max_send_us` | Sum and maximum of nonblocking socket-send calls |
| `tx_wait_us` | Observed sleep/rescheduling time after EAGAIN/EWOULDBLOCK |
| `tx_sleep_budget_us` | Requested sleep duration, capped by observed duration; excludes late rescheduling beyond the requested delay |
| `mem_wait_us`, `mem_errors` | ENOMEM/ENOBUFS retry sleeps and failed-send count |
| `other_wait_us` | Retry sleeps for other conditions, not automatically called network wait |
| `bytes`, `calls`, `retries`, `result` | Wire bytes queued, send calls, retries and handler result |

These are **wall times, not exclusive CPU times**. Preemption can lengthen
read/send calls. Do not sum overlapping parse/recv fields. Enqueueing all
bytes does not prove that the browser received or acknowledged them. A stall
before dispatch or after handler completion remains outside that measurement.

Browser tracing stores DNS/connect/TTFB/completion timings and CDP receive
timestamps/lengths, without response contents. It can identify a long gap
between received blocks or a connection delay. ICMP records correlate by host
timestamp but cannot alone prove a particular TCP transfer's failure cause.
It also records DOM/load events, long browser tasks, WebSocket creation/open,
handshake and first-message times, and the `getindex` send timestamp.
Optional `--netlog` saves Chromium network diagnostics privately in the output
directory; do not commit that file without a separate privacy review.

Board operation `/ws:getindex` now begins before reading the first frame byte.
Its `parse_us` marks the received/parsed command; `recv_us` includes frame reads.
Subtract `parse_us` from `total_us` to obtain the reply-generation/sending wall
time. Earlier captures began only after receiving the command and have no
dispatch fields. Slow (>=50 ms) or failed incoming frames use the fixed label
`/ws:recv`; no command values are logged. Slow or failed asynchronous WebSocket
sends are recorded as `/ws:send`; fast heartbeats are not logged individually.
An enclosing HTTP/getindex trace retains ownership of its counters. The
`last_errno` field distinguishes a closed socket, RAM errors and backpressure.
WS operation records are evidence for diagnosis, not automatically matched
HTTP resource exclusions.

Compact UART format is a JSON array after `WEBTRACE`, with this field order:

```text
id,path,start_us,total_us,parse_us,read_us,recv_us,send_us,max_send_us,
tx_wait_us,tx_sleep_budget_us,mem_wait_us,other_wait_us,mem_errors,
retries,bytes,calls,result,last_errno,select_wait_us,dispatch_us,dispatch_flags,
tcp_rx_us,tcp_rx_len,tcp_seq_gap
```

The analyzer expands it to named fields and retains all request records.
It also accepts the earlier 18/19/22-field arrays and verbose JSON-object format. The compact
format lives in DRAM to avoid repeated LX106 flash byte-load emulation while
formatting. No added task, stack or per-request heap allocation is used.

The browser records `performance.timeOrigin`. For a unique initial-state
operation between matched HTML and playlist requests, `startup` bounds the
time from the browser's command to server session entry. Bounds use HTTP
request-send/first-response timestamps, not assumed clock synchronization or
symmetric network delay. They handle 32-bit uptime wrap; ambiguous concurrent
operations or missing data are not guessed. The bound, dispatch time and frame
receive time distinguish delays before service, earlier server work, and reads.
They do not by themselves prove packet loss or authorize sample exclusion.

An optional `LWIP_HOOK_TCP_INPACKET_PCB` timestamps port-80 TCP payloads
before TCP input processing. It returns success unconditionally, does not
change packets, and records no payload bytes. A fixed 128-byte/eight-port
table is shared under short critical sections, with no log output from the
TCP task. `tcpInputToSessionMs` separates lwIP arrival from HTTP service.
The most recent payload is not necessarily the command: inspect length,
sequence gap and browser timeline, especially with pipelined/segmented data.
This hook is wired through CMake only for WebProfile; no downloaded SDK is
modified. Ordinary builds have neither the hook nor its table.

A large command-to-session delay with small TCP-input-to-session delay means
the delay preceded this lwIP input hook. That still includes Wi-Fi/driver
delivery and TCP-task scheduling, not only RF transit. A large post-input
delay instead points inside TCP/readiness/server scheduling. Neither case
automatically counts as an excluded network sample.

## Excluding network waits without hiding regressions

The report always keeps `raw` end-to-end statistics, all failed attempts and
each original sample. The separate `processingSample` may exclude an attempt
only when a matched, successful response is dominated by an explicitly
measured socket-backpressure sleep budget: at least 200 ms and at least half
the server wall time. Memory-pressure/other retries invalidate that decision.
All resources must have unique matching traces; another slow/unresolved
resource, request failure or memory error keeps the entire attempt included.
Removing the largest proven wait budget must also leave at most 500 ms;
several potentially overlapping resource waits are not summed to hide a
separate browser or dispatch stall.

Every exclusion has an explicit reason and count. EAGAIN means the socket
could not enqueue bytes; it does **not** prove RF loss. Receiver behavior,
TCP flow control or lwIP can also cause backpressure. Unknown causes, long
nonblocking send calls, ICMP loss alone and late task rescheduling are not
automatically excluded. Subtracting the bounded sleep budget from handler
wall time is labeled accordingly, never called CPU time.

Controls keep their raw server-confirmed timings. `/ws:volume` traces retain
session start, parse, TCP input and response timing for each volume command,
without logging its payload. The browser records a monotonic click timestamp,
time origin and the page-load anchor. The analyzer associates a command only
when one trace fits the HTTP-bounded clock interval; duplicates, concurrent
ambiguity, missing anchors and intervals over two minutes remain unmatched.
It adds an explicit five-millisecond drift allowance, not an assumed precise
clock synchronization. No controls are excluded by this association or by
analogy with a different HTTP request. The 500/200 ms end-to-end goal remains
distinct from the filtered processing sample. Per-command UART logging can
perturb the next command: verify improvements with profiling disabled too.

## Observer overhead and validation

UART output happens after handler completion but can delay the next request.
The first verbose trace added noticeable overhead: an 18-load diagnostic run
had four loads at 507-547 ms, while matching send waits were only 0-14 ms.
None was excluded. Compact records replace those verbose log lines; always
compare against the retained non-profiled image for performance claims.
The previous uninstrumented 3440.5 ms outlier cannot be retroactively
classified as network waiting.

Host tests compile the actual trace code, check timer wrap, separate memory
and socket retries, preserve errno, omit query data, and verify conservative
sample filtering (including duplicate/missing traces, late rescheduling and
ICMP loss). Run `node --test tests/esp8266-http-trace.test.js` alongside the
HTTP and WebUI regressions. Physical results are retained with the latency
reports, not replaced by synthetic test results.
