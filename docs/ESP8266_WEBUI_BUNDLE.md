# Shared WebUI bootstrap bundle (ESP8266 native)

The build generates gzip player and settings HTML responses from the existing
shared index, theme, stylesheet, scripts, page fragments and logo. No playlist,
credentials or saved setting values are compiled into them. Shared JavaScript can consume
explicitly preloaded fragments; other firmware keeps its existing fetch path.

The bundles serve only station-mode player/settings pages after checking
the compressed SPIFFS assets against the build fingerprints. Uploading any
WebUI asset invalidates them immediately. Missing or modified files,
AP configuration and maintenance pages retain their existing routes. Reboot
revalidates files. HTTP encoding negotiation supports qvalues and exclusions,
with `Vary: Accept-Encoding`; the response closes after transmission.
See [RFC 9110 section 12.5.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-12.5.3).

The generated data lives in flash, sent through the existing 512-byte scratch
buffer. No complete playlist or HTML buffer is allocated in device RAM.
Build command: `tools/esp8266_audio_profile/build_spi_pdm_debug.ps1`.
Regression tests: `node --test tests/esp8266-web-bundle.test.js tests/webui-cache-policy.test.js`.

## Physical result, 2026-09-08

GPIO13 SPI-PDM ordinary radio, stopped, 511 stations, one fresh Edge context
per cold load. Three cold + three warm loads: 570.3–603.3 ms in five runs,
1596.4 ms in one run (root response itself took 1198 ms). Previous healthy-link
results were about 890–920 ms. This is an improvement, **not the 500 ms goal**.
The complete player now makes two HTTP requests: root and current playlist.
Playlist transfer remains 324–373 ms. Thirty actual volume-button responses
confirmed over WebSocket took 8.0–18.3 ms; this does not yet prove Play/Stop.
All loads showed 511 rows and no JavaScript/resource errors.

RSSI during these loads: -63 to -74 dBm; startup -73 dBm after association
retries. User reports six metres, one wall and a wooden door. These observations
do not identify RF signal as the sole reason for latency outliers.
Raw results: `tests/results/esp8266-webui-latency-20260907/bundle-radio.json`.

## Bounded playlist reads

The follow-up uses direct POSIX reads of at most 1087 bytes into the existing
HTTP buffer, retaining only an incomplete row. Filtering and row fragmentation
remain identical to the index's 672-byte fgets buffer. Output chunks are still
512 bytes; no whole-playlist allocation and no extra DRAM. Actual-handler host
tests compare against fgets at ordinary, oversized and read-boundary records.

Do not use unbuffered `fread` here: this SDK's FILE path made the otherwise
correct experiment take 13.9–14.2 seconds per playlist. It was rejected.
Direct `read` reduced healthy transfers from 324–373 to 284–288 ms (one 322 ms),
with all 511 rows preserved. Full readiness remained 524–600 ms: still above
target. Play/Stop tests additionally exposed 248–291 ms stop status and
515–566 ms station-index updates, consistent with successive 250 ms polls.
Raw results: `tests/results/esp8266-webui-latency-20260907/posix-read-radio.json`.

## State-change notifications

State changes now notify the existing app task after releasing the state mutex;
audio never performs HTTP transmission. Bitrate/RSSI-only changes retain the
two-second heartbeat. The HTTP task sends station status and index in order
within the same poll. This SDK copies a WebSocket payload before returning
from `httpd_ws_send_frame_async`, so no second persistent buffer is necessary.
The compiled host test verifies unlocked notifications and no per-frame wakeup.

The first physical run had 50% ping loss (3/6) and severe outliers, despite RSSI
sometimes reaching -61 dBm. After a reset **without any firmware change**, the
repeat measured RSSI -55..-57, volume 8.4–11.5 ms, Play confirmation 45.2 ms,
Stop 27.1–45.0 ms, station confirmation/selection 32.5–50.0 ms. Four stream
starts reached the playing state 290–326 ms after confirmation; this is separate
from command acceptance. Cold/warm page readiness 546.4/531.8 ms still fails
the page goal. Keep both runs, not only the successful one:
`event-state-radio.json` and `event-state-repeat.json` in the results directory.
The network-delay cause is not conclusively isolated by these measurements.

## Fixed-length flash response

The root bundle now uses Content-Length instead of chunked framing. The HTTP
server stages at most 1024 bytes at a time in its existing scratch area,
aligning the staging pointer without allocating RAM. This keeps XIP byte reads
out of lwIP and removes per-chunk formatting. A host test sends 8193 binary
bytes through deliberately unaligned scratch storage, checks exact framing,
the 1024-byte send bound and propagation of an interrupted transfer.

Three cold + three warm physical loads: 1097.4, 451.5, 451.8, 447.0, 444.0,
447.3 ms. The first root request alone was 751 ms; it remains a recorded
failure. All 48 button confirmations passed (maximum 51.5 ms). Twelve stream
starts reached fresh codec metadata and playing state 275–373 ms after command
confirmation. Earlier reports could mistake an old playing flag for a newly
decoded station; the benchmark now also requires nonempty new stream identity.
Raw result: `bundle-fixed-radio.json`. The rejected/intermediate 1 KiB chunked
run is also retained as `bundle-1k-radio.json` (503–529 ms page readiness).

The broader browser audit passed 54 functional assertions: AAC 320 kbps,
MP3 ROCK FM / Europa Plus, search, commands, settings readback, mobile layout,
maintenance GET routes, two concurrent tabs and bidirectional volume updates.
Two-tab confirmations were 46–59 ms. Playback HTTP status requests were 27–37 ms.
Minimum observed heap 11272 bytes; HTTP stack high-water headroom 2212 bytes.
Station 1, volume 254 and stopped state were restored. No OTA/upload/reset was
tested by this audit. Settings navigation still took 2155 ms, reload 1705 ms.
Its per-setting timings include an intentional 200 ms test wait, so are not
valid 200 ms latency measurements. The audit also logged one caught WebUI
exception because its initial getsystem request reached the player page before
the settings-only radiolink element existed. This remains to be addressed;
54 passing assertions do **not** mean a completely error-free UI.
Raw result: `fixed-full-audit.json`.

## Follow-up, 2026-09-08

Settings now also use the shared bundle. Null-DOM exceptions in system and
station messages are fixed. The old settings audit's 1.7–2.2 s included an
intentional 1.5 s pause; a dedicated readiness observer now measures actual
saved values/capabilities/Wi-Fi loading. Exact retained image: 242–276 ms.
Playback/concurrent-load stress exposes a remaining long playlist handler;
the complete 500/200 ms goal is still open. See
[updated results](ESP8266_WEBUI_LATENCY_RESULTS_2026-09-08.md).
