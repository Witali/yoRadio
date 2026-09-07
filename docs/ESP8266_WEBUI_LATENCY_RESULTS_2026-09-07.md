# WebUI latency: first measured improvements

Physical Wemos D1 mini, ESP8266 160 MHz, QIO40, ordinary native radio with
temporary SPI-PDM8 on GPIO13/D7 (384615 bit/s). Not the isolated tone firmware.
Application-only flashing; Wi-Fi, playlist, NVS and OTA layout preserved.
Computer Wi-Fi configuration was not changed.

## Network findings

Initial series after restoring radio: RSSI -70..-74 dBm; ICMP 15/15 replies,
2..8 ms, mean 3 ms. Twelve separate TCP/HTTP status connections established in
3..9 ms; ten responses approximately 16..22 ms, two 228/236 ms.

Later RSSI varied -67..-78 dBm. Several resets had association/authentication
failures before getting DHCP at about 20 s. Logged SDK reasons: 4 ASSOC_EXPIRE,
6 NOT_AUTHED, 204 HANDSHAKE_TIMEOUT and 205 CONNECTION_FAIL. These are evidence
of connection instability, not proof that weak RSSI is the sole cause.

The preceding I2S session had TCP connect timeouts and lost pings even with
RSSI -67..-70. This is not a controlled I2S/SPI comparison: firmware and board
reset also changed. Do not attribute it conclusively to the GPIO3 connection.

## Browser measurements (radio stopped, one tab)

Headless Edge/Playwright; completion requires populated playlist, selected
station, open WebSocket, rendered logo and hidden startup spinner. A fresh
browser context is used for each cold sample; warm samples reuse the context.
All samples have 511 visible playlist rows and no JS/resource errors.

| Measurement | Baseline | Buffered read + ASCII filter |
|---|---:|---:|
| Cold full player, ms | 1142.5, 1094.0, 1104.4 | 917.0, 888.4 |
| Warm full player, ms | 1098.2, 1113.8, 1116.2 | 907.4, 908.9 |
| Playlist request in page, ms (includes queueing) | 639..649 | 437..440 |
| Volume button server confirmation, ms | 8.1..11.2 (30 actions) | 8.3..14.7 (20 actions) |

Volume is restored to its original 254 after testing. Timing starts in the
page before dispatching its real button click; completion requires a changed
volume from a received WebSocket payload and matching DOM readback, not just
an optimistic slider change.

Raw reports: `tests/results/esp8266-webui-latency-20260907/`.
Threshold failures intentionally produce a nonzero benchmark exit status.

## Changes retained

1. Removed unconditional sleeping after each 512-byte HTTP chunk. The socket
   writer still blocks/yields on actual backpressure and has one overall
   response deadline. Alone this saved only about 40 ms of full-page time.
2. Explicit 416-byte stdio read-ahead reuses the tail of the existing 1088-byte
   WebSocket status workspace while the HTTP task serves the playlist. A
   672-byte row and independent 512-byte output buffer remain bounded. No
   whole-playlist allocation and no extra global RAM. `setvbuf` precedes all
   stream operations, and the FILE is closed before reuse as status storage.
3. Filter URLs using one ASCII scan and immediate extension codes, avoiding
   `strpbrk` and case-folding flash-byte reads in libc. ESP8266 SDK's
   `components/esp8266/include/ibus_data.h` documents the slow LoadStoreError
   emulation for byte reads from IBus flash; the ELF map places these strings
   and libc's `_ctype_` table at 0x402... . No additional RAM table is used.
4. Optional `-WebProfile` build flag records playlist read/send wall times.
   Disabled by default; it does not select a different functional path.

Intermediate on-board profile: before read buffering total 523 ms, read
249..250 ms, send 149..150 ms. With explicit buffering total 412..423 ms,
read 130..145 ms, send 145..175 ms. After ASCII filtering, isolated successful
playlist HTTP requests were about 350..387 ms instead of 535..542 ms.
These wall times include preemption; they are not pure CPU-cycle measurements.

Slow attempts are not discarded: one intermediate initial request spent
15 seconds establishing access while the board acquired Wi-Fi; another load
was 3590 ms. The buffered series also had one 3159 ms playlist response
(profile: send 2883 ms). The final isolated request series started with an
856 ms outlier. Healthy-link averages do not guarantee a real-time deadline.

## Correctness and remaining work

- 31 regression tests passed for real C playlist streaming/HTTP framing,
  filtered rows across buffer boundaries, early send failure, empty files,
  missing final newline, WebUI playlist selection/reconnect and network state.
- 1120 extension combinations compare the new filter with the previous
  algorithm (case, query/fragment, suffixes), plus short URLs and UTF-8 rows.
- **500 ms page target is not met.** The page still serially requests shell,
  variables, CSS/JS, player fragment, logo and playlist; consider a generated
  compressed bootstrap bundle from the same assets, without forking the UI.
- Play/Stop, next/previous, settings, playing-radio and two-tab latency are
  still to be measured against 200 ms. The current main loop may defer status
  polling up to 250 ms; state-change notification is a candidate to test.
- Do not call the goal complete based on volume buttons alone or a cached
  shell. Repeat cold/warm measurements and retain maxima and failures.
