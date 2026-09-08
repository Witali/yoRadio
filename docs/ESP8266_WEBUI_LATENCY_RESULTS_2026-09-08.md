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

The last batch failed an HTTP status fetch and ended early; this is retained
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
