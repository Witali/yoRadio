# Shared WebUI bootstrap bundle (ESP8266 native)

The build generates one gzip HTML response from the existing shared index,
theme, stylesheet, scripts, player fragment and logo. No playlist, credentials
or settings are compiled into it. The ordinary shared JavaScript can consume
explicitly preloaded fragments; other firmware keeps its existing fetch path.

The bundle is served only for the station-mode player and only after checking
the compressed SPIFFS assets against the build fingerprints. Uploading any
WebUI asset invalidates it immediately. Missing or modified files, settings,
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
