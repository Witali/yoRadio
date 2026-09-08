# ESP8266 WebUI: settings and playback-load stress, 2026-09-08

The 500 ms page / 200 ms confirmed-control goal remains **open**.
Normal radio uses the user's temporary SPI GPIO13/D7 wiring, not the isolated
tone generator. CPU160/QIO40, HTTP port 80, two WebSocket subscribers. No PC
Wi-Fi changes. Measurements use headless Edge/Playwright; the embedded browser
helper was unavailable. Source, actual firmware and raw reports are retained.

## Retained changes

- `c6e4427`: shared JS accepts system settings on the player without dereferencing
  an absent `radiolink`. Browser audit now fails on recorded console errors too.
- `d2c5de9`: settings page uses the exact common compressed assets, embedded as
  a flash-only bundle. Runtime SPIFFS fingerprints, upload invalidation, gzip
  negotiation and Wi-Fi-only AP fallback remain in force. No saved settings,
  playlist or credentials are embedded. Adds about 26 KiB flash, no large RAM.
- `6bb08e8`: station broadcasts are valid on settings pages without a playlist
  DOM. They still update the current station; no caught exception.
- `30ec6d3`: real AAC/MP3 decoding, reloads and concurrent-tab control benchmark.
- `32d8978`: bounded output block grows 512 -> 1024 bytes; +512 static RAM,
  no new task, stack or full-list allocation. Input stays bounded at 1087 bytes.

## Corrected measurement methodology

The previous full-audit settings timing of 1.7–2.2 s included an intentional
1.5 s test sleep. It must not be interpreted as actual page readiness.
`test_esp8266_settings_latency.cjs` now timestamps navigation until all six
settings/capability responses, logo, successful Wi-Fi fetch and matching form
values are present. It records no SSIDs, passwords or Wi-Fi response bodies.
Settings button timings wait for device acceptance **and** a fresh saved-value
readback, not just the optimistic checkbox update. The test restores its value.

`test_esp8266_webui_latency.cjs --stress` keeps decoding AAC (~320 kbps) and
MP3 (128 kbps), reloads the player, and issues volume clicks while a second
tab loads. Status checks require decoding to remain active and record RSSI,
free/minimum heap and HTTP stack headroom. Station 176, volume 254 and stopped
state were captured before tests and are restored by the runners.

## Direct comparison

| Scenario | Before | After |
|---|---:|---:|
| Settings, cold/warm, no artificial wait | 531–534 ms | 217–274 ms (fixed JS) |
| Settings acceptance + saved-value readback | not measured | 14.8–29.2 ms |
| Stopped player, 512 -> 1024 output block | 466–475 ms | 424–467 ms |
| Player reload, AAC active | 699 ms | 661 ms |
| Player reload, MP3 active | 693 ms | 659 ms |
| Second tab loading, AAC active | 765 ms | 712 ms |
| Second tab loading, MP3 active | 758 ms | 686 ms |
| Slowest control during second-tab load | 370 ms | 310 ms |

These are actual runs, not matched RF laboratory conditions; RSSI varied
between about -66 and -76 dBm during stress. The 1-KiB comparison image had
optional per-request profiling; the retained image disables it. Keep all
outliers rather than choosing only runs that meet the target.

Serial profiling of the 1-KiB variant: playlist handler 231–234 ms stopped,
377–391 ms playing. Of the latter, reads took 96–123 ms and sends 201–225 ms;
the remainder includes filtering/copies and scheduler interruptions. These
are wall times, not exclusive CPU times. The synchronous handler prevents
the HTTP task from dispatching queued WebSocket commands until it returns.
This explains why ordinary volume responses are ~15 ms but a concurrent
download can delay them by hundreds of milliseconds.

Minimum heap sampled in stress: 8668 bytes before, 8872 bytes after; this is
not evidence the larger buffer saves memory (the fixed cost is +512 bytes,
and dynamic network allocations vary). HTTP stack headroom remained >=2244
bytes in the baseline and >=2316 in the profiled run. No decoded-audio stop
or browser exception occurred in those stress samples.

## Reproduction and next work

Final non-profiled image `32d8978`: 759520 bytes, SHA-256
`9ED938C2AD147FABBE4C341ED265D9C5C4765C8B218B73D13F00758D978CE3A8`,
saved under `firmware/development/esp8266-spi-pdm-debug/app.bin` and flashed
at app0 0x10000. All 52 host regressions and 54 functional browser checks
pass, with no recorded JavaScript errors. Initial scrolling to station 176
is verified independently of the intermediate smooth-scroll screenshot.

Exact-image results: stopped player 430.4/450.2 ms; settings 241.7–276.2 ms,
12 acceptance-plus-readback checks 14.9–22.6 ms. Playing page loads: AAC
712.2 ms, MP3 649.1 ms; concurrent 755.3/682.2 ms. Three of 56 confirmed
controls still fail (290.6 ms concurrent AAC, 229.9 ms ordinary MP3, 210.6 ms
concurrent MP3); all four decoder-start waits succeed. Thus not every outlier
can be attributed to a concurrent static request. Minimum heap after all
tests 8804 bytes, HTTP stack headroom 2212 bytes. Final status: station 176,
stopped, no error, RSSI -69 dBm. Do not reset away this evidence.

Report names identify their stages: `settings-before` is the old unbundled
settings page; `settings-bundle` still contains one caught station-message
error, fixed in `settings-fixed`; `player-bundle` uses 512-byte output blocks;
`stress-before` versus `stress-1k` compares the output-block change (the latter
includes profiling); `retained-*` all use the exact non-profiled image above.

Use the same installed runtime/Playwright and Edge as the other board tests:

```text
node tools/test_esp8266_settings_latency.cjs --rounds 3 --controls --output <dir>
node tools/test_esp8266_webui_latency.cjs --rounds 3 --controls --playback --stress --output <dir>
node tools/test_esp8266_webui_browser.cjs --host 192.168.100.6 --output <dir>
```

Await DHCP before timing. Failed initial Wi-Fi associations are logged
separately; do not include an intentional reboot in navigation latency.
Do not reset the board between ordinary repeated loads to hide degradation.

Next bottleneck: avoid repeated raw CSV parsing/transmission on every fresh
browser load. Evaluate a persistent validated compressed representation rebuilt
on playlist change, then bounded resumable sends if commands can still wait
over 200 ms. Preserve the original filtered rows, selection indices and fresh
uploads; do not solve this with a cached stale list or a full-playlist RAM buffer.
Repeat stopped/playing, one/two tabs, settings and all real player controls.

Raw JSON is in `tests/results/esp8266-webui-latency-20260908/`; private serial
logs and screenshots remain in `.build/webui-diagnostic-20260908/`.

## Optional upload-time playlist gzip (later, source b74e21b)

The earlier images above have been superseded in the replaceable development
directory; their hashes and source revisions still identify those results.
Current non-profiled gzip image: 768112 bytes, SHA-256
`EA7C6F830A944DB0BCDC0830F4A376E36E5A3C29F94D8FBC3A1EDF43430DA0BE`.
Matched OFF build: 761328 bytes; configs differ only in the gzip option.
OFF was compiled and symbol-checked, not flashed. Implementation/configuration
and memory/flash costs: `ESP8266_PLAYLIST_WEB_GZIP.md`.

- Full original CSV 53808 bytes; supported HTTP CSV 36086 bytes, gzip 12637.
  The full source and station index remain authoritative. Cache workspace
  4320 bytes is transient, not an allocation per page or per station change.
- A real same-size name edit, identical upload, and full original restoration
  passed. HTTP 303 is the expected upload success response. Gzip and identity
  decode to the same filtered content. Retained-image reboot reused the cache.
- Exact non-profiled image: 18 page loads, 17 within 500 ms (249.5-416.3 ms),
  one AAC-playing load **3440.5 ms**. That request's playlist transfer took
  2780.9 ms; it predates causal tracing and is not classified/excluded.
- All 168 player control confirmations passed, maximum 158.9 ms; 12 separately
  measured decoded-audio starts passed. Six settings loads 200.3-220.4 ms,
  18 acceptance/readback checks <=30.7 ms. Full browser audit: 54/54, no JS
  errors. 57 host checks passed before adding the tracing tests; 59 afterward.
- Minimum free heap after the full physical audit was 7928 bytes; HTTP stack
  headroom 2212 bytes. These are observed minima, not guaranteed reserves.
  Station 176 / volume 254 / stopped restored. PC Wi-Fi unchanged.

Reports: `playlist-gzip-{player,settings,browser,upload}.json`.

## Causal tracing and retained failures

Per user request, `YORADIO_ESP8266_WEB_PROFILE` creates a separate diagnostic
image and correlates browser resources with board records. It distinguishes
file reads, receives, nonblocking send calls, EAGAIN sleep, RAM retries and
late rescheduling. A separate processing sample may exclude only explicitly
confirmed dominant TX waits; raw end-to-end results are always retained.
No recorded batch below qualifies for automatic exclusions.

| Diagnostic batch | Loads | Page max / failures >500 ms | Controls | Control max / failures >200 ms |
|---|---:|---:|---:|---:|
| Verbose trace, aa748bf | 18 | 546.6 ms / 4 | 168 | see raw JSON |
| Compact trace, 514ece0 | 36 | 1690.2 ms / 17 | 336 | 298.1 ms / 7 |
| Added browser handshake timeline, same image | 7 before interruption | 697.7 ms / 5 | 72 | 827.7 ms / 2 |
| getindex/slow-WS trace, fa842ef | 12 | 1348.1 ms / 7 | 112 | 256.0 ms / 1 |

The handshake-timeline batch failed an HTTP status fetch and ended early; this is retained
as an error, not a passing shorter run. A later UART warning reported failed
WebSocket header sending. The captured script restored station 176/stopped.
Optional `--netlog` remains private under `.build`, not committed.

In the compact 1.3-1.7 s samples, HTML and playlist bodies had no comparable
pause: largest receive gaps were roughly 6-19 ms. Much of the time was
between HTML completion and the subsequent playlist request. The added
timeline found both a slow WebSocket opening and a roughly 250 ms delay
between opening and the first status message, with no browser long task in
those samples. This does not establish a weak Wi-Fi signal as the sole cause.
Independent ICMP: 350 samples, 2 failures, successful RTT maximum 24 ms.

Detailed UART logging itself perturbs timings after each handler. Compact
records reduce wire output and flash-format overhead, but diagnostic runs
are not interchangeable with a non-profiled performance run. Firmware
`fa842ef` further traces `getindex` processing and slow/failed asynchronous
WebSocket sends, including errno, to localize the remaining gap. See
`ESP8266_WEBUI_TRACE.md`; keep the 500/200 ms goal open.

Exact `fa842ef` image: 769504 bytes, SHA-256
`514E0D61CE3A67353C9B3B7DE5F019F66A98C92743537EAA329A3DA7EE437F03`,
saved in the separate `esp8266-spi-pdm-debug-web-trace` variant and flashed.
Twelve `getindex` operations took 14.4-26.6 ms each, without EAGAIN sleep or
memory errors; no slow async-send record appeared in this particular run.
Browser command-to-first-message latency could still reach about 250 ms.
Those observations narrow the interval but do not distinguish delayed TCP
delivery from request dispatch waiting; they are not a reason to exclude
these samples. No JS/test exception in this last run. Final station 176,
volume 254, stopped, no error; free heap 25996, observed minimum 7532 bytes,
HTTP stack headroom 2228 bytes. All 59 host regressions pass.

Next: correlate the receipt/dispatch of the first WebSocket command with
browser frame-send and frame-receive times; inspect TCP delivery/ACK behavior
and queued work. Do not call the remaining delay pure network waiting until
that interval is identified. The old uninstrumented 3.44 s case remains open.

## Dispatch/input trace: an actual protocol failure, not network waiting

Source `bf530f3`, 769696-byte diagnostic application, SHA-256
`4258A7118F9731CFA4D80E5FD7FBA0EE86E22AD78FB9291CA3192628282D3C89`,
flashed app0 and verified. Initial connection retried, DHCP at about 20 s,
RSSI -72 dBm. No PC Wi-Fi changes.

The first cold page was ready in 368.5 ms. Its command reached session
processing within the bounded interval 0.8-13.6 ms; select-to-session delay
0.281 ms, frame parsing 1.317 ms, complete operation 16.289 ms.
Later, both AAC page attempts timed out: Chromium repeatedly reported
`Could not decode a text frame as UTF-8.` and reconnected every two seconds.
The run ended with an error; do not interpret its one finite page timing as
a successful one-sample benchmark. All failed button/page attempts remain.

A separate bounded raw WebSocket capture reproduced invalid byte `F1` in
the ICY performer's name (`50 6c f1 63 69 64 6f`). The station name in the
same frame had valid UTF-8. The JSON encoder passed this byte through as a
text frame. The browser then reset the connection; UART recorded errno 104,
not EAGAIN or a memory retry. This is a concrete newly observed failure,
not proof of the cause of the older 3.44 s sample.

RFC 6455 section 8.1 requires failing an invalid-UTF-8 connection; RFC 8259
section 8.1 requires UTF-8 for interoperable JSON. Sources:
[WebSocket](https://www.rfc-editor.org/rfc/rfc6455.html#section-8.1),
[JSON](https://www.rfc-editor.org/rfc/rfc8259.html#section-8.1).

Reports `trace-dispatch-{browser,analysis}.json` retain the failure. Zero
network exclusions. The original private byte capture stays under `.build`;
the host regression uses only the minimal malformed-name byte sequence.
Station 176 and stopped were restored. A later readback found volume zero:
the failed-page benchmark had read the uninitialized slider and restored its
default rather than the original value. The later one-shot diagnostic also
used an unsupported `vol` command, so its claimed volume restore was not
verified. Volume was subsequently restored using `volume=254` and confirmed
in a server reply. The benchmark now stops controls after failed readiness.
The remaining first-command delay still needs investigation.

## UTF-8 repair and more precise wait evidence

Source `fa1abc1`, application 769952 bytes, SHA-256
`3427ACBFAEC7732FC5DE3EF7DF86D7602BEFC4136D715B79BC09B118289F7DF8`,
flashed and hash-verified. The byte-wise JSON writer is now code-point-aware:
valid UTF-8 is unchanged; invalid bytes become ASCII `?`, without guessing a
legacy charset. The title and full status are still sent, including messages
that happen to contain JSON-looking text. Quotes/backslashes are escaped
atomically, and bounded buffers never end halfway through a valid UTF-8
sequence. The existing omission of ASCII controls is unchanged. No extra
heap/message buffer; the worst-case 2x escaping bound is retained.

Initial repaired-image run: 18/18 pages became ready, no WebSocket UTF-8 errors
or JavaScript exceptions. Page times 304.4-527.5 ms, 3 above 500 ms. There were
15 false control timeouts from asking minus-at-zero to change the value;
the old raw report is retained, not relabeled as passing or network waiting.
The test now alternates inward first at either volume boundary and has a
regression for 0/1/2/128/253/254. Subsequent tests start at the confirmed 254.

The 527.5 ms cold load has a command-to-session interval bounded at
209.6-222.8 ms. The server spent 211.436 ms in select; readiness-to-session
was 0.304 ms, frame parsing 1.296 ms, complete initial reply 17.144 ms. This
rules out a 200 ms delay in this handler, but does not separate TCP delivery
from a delayed readiness notification/rescheduling. It is not automatically
excluded. Next investigate the TCP/readiness interval using targeted packet
evidence; do not optimize reply construction as the cause of this sample.

Reports: `trace-utf8-{browser,analysis}.json`. The image passed all 61 host
checks before the added benchmark boundary regression (62 checks afterward).

Repeat with corrected test at volume 254: 18 page loads, 285.3-503.2 ms;
three above 500 ms. All 168 server-confirmed controls passed, maximum 77 ms;
all 12 separate audio starts passed. No JS exceptions or WS frame errors,
no automatic network exclusions. Reports `trace-utf8-repeat-{browser,analysis}.json`.
Final station 176/stopped, volume 254 (confirmed WS readback before the run,
restored by each completed button cycle). Free heap 25684, minimum 8044,
HTTP stack headroom 2268 bytes, RSSI -74 dBm.

The non-profiled variant also builds with the UTF-8 fix: 768352 bytes,
SHA-256 `66FC91DACD703B768228D427616CD6106964B0BF370F1D1DF8BFCCB7118C86BF`,
source `a639709`. This new non-profiled binary is compile-verified only;
the board retains the `fa1abc1` diagnostic image for the 200 ms investigation.

## TCP-input trace excludes audio decoding in the reproduced idle stalls

Diagnostic source `14e1526`, 770688 bytes, SHA-256
`B4F040752763A8DF6839943250795B9A9E33A184CFBEE85B44AA3408E996157A`,
flashed app0/hash verified. A supported lwIP input hook timestamps only port-80
TCP payload metadata; no SDK source patch, packet changes or new task. Windows
PktMon denied driver access without administrator rights; no packet capture or
PC network configuration was changed.

After reset, the test never started playback: 40/40 page states were stopped,
zero control commands, no codec/bitrate in status before or after. The audio
task blocks in `xQueueReceive(..., portMAX_DELAY)` until a command. Wi-Fi modem
sleep is already disabled both while stopped and playing.

- Cold round 10: page 513.4 ms; command-to-session 220.4-232.6 ms; select
  222.255 ms; TCP-input-to-session **1.162 ms**; frame input 16 bytes, in-order
  (`tcp_seq_gap=0`); command parsing 1.572 ms; complete reply 17.798 ms.
- Cold round 13: page 492.1 ms; command-to-session 210.3-221.2 ms; select
  209.096 ms; TCP-input-to-session **1.172 ms**, also an in-order 16-byte frame.

The delay precedes lwIP's input hook, not the web handler or audio decoding.
The hook does not expose physical RF arrival: client TCP buffering/retransmit,
Wi-Fi/driver delivery and TCP-task scheduling still require distinction.
Do not assert packet loss solely from the roughly 200 ms duration.

All 40 loads: 268.1-513.4 ms, p95 373.4 ms, one >500 ms; no JS/WS errors.
Zero automatic exclusions. Reports `trace-tcp-idle-{browser,analysis}.json`.
Final station 176/stopped, free heap 26096/min18804, HTTP stack free2272,
RSSI -60 dBm. Next reduce the unnecessary client `getindex` round trip while
retaining an actual server snapshot and legacy WebUI behavior.

## Opt-in initial snapshot: one fewer network round trip

Source `91889f4`, 772064 bytes, SHA-256
`C3EEAD9E4AA8D46E125A9FA66BBF3277129E7CCF9A23866E7D5E79343C2A4241`.
Flashed app0 and verified. The matching shared `script.js.gz` was uploaded
and its downloaded bytes verified (SHA-256
`31511ED52482AAF84ED412A505F5CFAFA67271C61FBA2A130A1BAA7448EDCF29`).
No partition, Wi-Fi, playlist or audio-output change.

The native player bundle opts into `/ws?initial=1`: the server sends its real
snapshot immediately after the upgrade. Other clients and settings retain
explicit requests. A bounded 16-message frontend queue handles the snapshot
arriving before the player fragment is installed; overflow requests a fresh
snapshot. Reconnection does not reuse an old pending snapshot. All 66 host
checks pass, including early/late arrival and legacy behavior.

Physical headless Edge results (raw samples, no exclusions):

| Run | Loads | Median | p95 | Maximum | Over 500 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| First snapshot-only idle | 40 | 282.9 ms | 368.2 ms | 1269.6 ms | 2 |
| Interleaved snapshot | 30 | 276.9 ms | 300.7 ms | 384.6 ms | 0 |
| Interleaved legacy, same image | 30 | 286.2 ms | 482.8 ms | 508.0 ms | 1 |
| MP3/AAC/two-tab stress | 18 | 412.4 ms | 486.5 ms | 486.5 ms | 0 |

The first 556.5 ms sample includes about 257 ms before playlist connection
setup. The 1269.6 ms sample delays the WebSocket handshake request by about
one second; the handshake itself takes about 14 ms. These remain unresolved,
not relabeled as network exclusions. Private Chromium NetLogs from an earlier
run also contain board TCP connect attempts lasting 1012 and 1019 ms; that
does not establish why those connections took so long.

Stress: 168 changed-state confirmations, two failures at 248.1/255.5 ms;
12 separate decoded-audio starts pass. AAC ~320 kbps and MP3 128 kbps were
confirmed by the device. Minimum heap 7664 bytes, HTTP stack headroom2228.
No JS or malformed WS text errors. Functional browser audit: 54/54 checks,
including two tabs. Settings: 18/18 acknowledged/read-back changes, five loads
230.7-263 ms and one 2605.4 ms outlier. This is not completion of the 500/200
ms goal. Reports are `initial-{idle,compare,stress,functional,settings}-browser.json`
plus idle/compare analyses. Next trace individual controls before optimizing
their processing; do not infer their cause from the separate idle experiment.

## Per-command trace during a degraded connection

Source `5c121bb`, 772128 bytes, SHA-256
`DD16D9E55D20873908BB5D4E9739199A6E48CA41A549A2733099448E4C902BAF`,
app0 flashed/hash verified. Diagnostic-only volume labels and browser
monotonic click timestamps allow bounded associations (including explicit
5 ms drift allowance); no request values or private payloads are logged.

The link degraded during this run. All raw failures are retained:
24 loads, median1870.4/max21232.1 ms, 17 over500 ms; 224 controls,
138 failed the200 ms/confirmation requirement, maximum finite3383.7 ms.
All16 separate decoded-audio starts passed; two browser send attempts
encountered a reconnecting socket. UART covers the first160 seconds only.
Later read-only ICMP sampling: 29 of33 replies timed out; four returned in
3/12/90/153 ms. The neighbor MAC matches the board. No PC network changes.
RSSI alone (-61 to -73 dBm) did not predict this failure.

Specific stopped-player commands:

- 1855 ms confirmation: command-to-handler1788.4-1813.0 ms,
  TCP-input-to-handler1.045 ms, handler12.707 ms, send7.148 ms.
- 983.8 ms confirmation: command-to-handler918.9-943.4 ms,
  TCP-input-to-handler1.023 ms, handler12.514 ms.
- Repeated ~1850 ms confirmations similarly precede TCP input; handler
  remains11.4-15.6 ms. No memory errors or TX retry sleeps in these commands.

This excludes audio decoding and handler computation as the source of those
long waits, not every possible stall. It does not distinguish radio loss,
driver/client buffering or scheduling before TCP input.

The initial root response also records real socket backpressure: 8.762 s
handler wall time, including6.381 s explicit EAGAIN sleep budget, 8605 retries,
no memory errors. The playlist records3.024 s sleep budget. The full page
takes19.016 s, leaving substantial other delays; the analyzer correctly
excludes **zero** whole samples instead of hiding the failure.
Reports: `volume-stress-{browser,analysis}.json`, `volume-link.json`.

One independent reduction is now implemented in source `1d36682`: reply to
volume changes with only Arduino's volume payload, not status/current/SD/mode
four-frame startup traffic. Actual device readback and other-tab updates are
preserved. The C regression covers every volume0-254, one send and return
errors; the shared frontend regression proves no station/playlist mutation.
All69 host checks pass. Hardware measurements without detailed profiling
follow separately; compilation alone is not a latency improvement claim.
