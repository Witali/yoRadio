# ESP8266: optional compressed WebUI playlist

Native ESP8266 firmware has a build-time option:

```text
CONFIG_YORADIO_PLAYLIST_WEB_GZIP=y
```

Default: **enabled**. In menuconfig: `yoRadio ESP8266 options` ->
`Cache a compressed WebUI playlist in SPIFFS`. Disable it in the active
sdkconfig (not only sdkconfig.defaults of an already configured build):

```text
# CONFIG_YORADIO_PLAYLIST_WEB_GZIP is not set
```

This option controls the playlist representation only, not compressed
HTML/JavaScript/CSS assets. It does not change audio pins, codecs or partitions.
Arduino, C3 and CYD behavior is not changed by this ESP8266-specific option.

## Build both variants

Using the existing toolchain and temporary SPI GPIO13/D7 profile:

```powershell
powershell -File tools/esp8266_audio_profile/build_spi_pdm_debug.ps1
powershell -File tools/esp8266_audio_profile/build_spi_pdm_debug.ps1 -NoPlaylistGzip
```

The script saves separate images under `firmware/development/`:

| Variant | Gzip | Output directory |
|---|---|---|
| Normal SPI radio | ON | `esp8266-spi-pdm-debug` |
| Raw playlist comparison | OFF | `esp8266-spi-pdm-raw-playlist` |

It checks the actual cached sdkconfig and records `playlist_web_gzip` in the
manifest. Building does not flash the board. The normal board-default I2S
output is unchanged; these two comparison profiles use the user's temporary
SPI wiring. With OFF, CMake excludes both encoder and cache source files.
An existing cache in SPIFFS is ignored, not deleted automatically.

## Storage and upload behavior

- `data/playlist.csv` remains the full authoritative file, with its existing
  station-offset index. The decoder never decompresses a playlist to select
  the next/previous station.
- After a valid upload is installed and indexed, firmware builds the filtered
  WebUI representation **before returning the upload response**. It does not
  gzip each HTTP download and does not allocate the entire playlist in RAM.
- At boot, source size/CRC and cached-body size/CRC are checked. An unchanged
  valid cache is reused without rewriting flash. Missing, stale or damaged
  data causes a rebuild. An identical upload also validates/reuses the cache.
- The internal `data/playlist.csv.web.gz` file has a 24-byte validation header
  followed by a standard gzip stream. The header is NOT sent over HTTP; this
  internal file is not itself a standalone `.gz` archive. Temporary and backup
  files protect replacement. The cache format/version must be bumped when the
  station-filter policy changes.
- Browsers accepting gzip receive `Content-Encoding: gzip` and
  `Vary: Accept-Encoding`. Identity clients get the same filtered CSV streamed
  in bounded blocks. If compression fails, space/RAM is insufficient, or the
  list would not shrink, firmware falls back to identity when acceptable.
  Explicitly excluding every available representation returns HTTP 406.

The compressor uses a 512-byte LZ77 history, one hash candidate, fixed Huffman
DEFLATE, CRC32 and the gzip size trailer. File/HTTP output is bounded; no new
task or worker stack is introduced. Formats:
[DEFLATE, RFC 1951](https://www.rfc-editor.org/rfc/rfc1951.html),
[gzip, RFC 1952](https://www.rfc-editor.org/rfc/rfc1952.html).

## Measured costs, 2026-09-08

Matched sdkconfigs differ only in this option, source `b74e21b`:

| Item | Bytes |
|---|---:|
| Application with gzip ON | 768112 |
| Application with gzip OFF | 761328 |
| Image-size difference | 6784 |
| Temporary cache-generation workspace on ESP8266 | 4320 |
| Full source CSV | 53808 |
| Filtered HTTP identity CSV (511 stations) | 36086 |
| Gzip HTTP body | 12637 |
| Cache validation header | 24 |

The wire playlist shrinks by about **65%**. The 4320-byte workspace is freed
after refresh; stdio/file-handle allocations are additional transient costs,
not included in that figure. Flash needs space for a replacement and the
existing cache during update. This is a speed optimization, not removal of
the authoritative CSV from flash.

First cache generation took about 1.34 s; rebuilding after upload about
2.1-2.4 s in serial observations. A retained-image reboot logged `Validated
gzip`, not a rewrite. Complete HTTP upload/validation/index/cache cycles took
7.8-12.7 s; these maintenance operations do not meet the player-button latency
target. One same-session GET comparison: gzip 88.9 ms, identity 238.2 ms.

The ON image is flashed and tested. OFF is compiled and symbol-checked, not
flashed. Repeated exact-image player results: 17/18 loads <=500 ms, one
3440.5 ms outlier; all 168 control confirmations <=158.9 ms. This improvement
does **not** yet prove the complete 500/200 ms goal. Full evidence belongs in
`ESP8266_WEBUI_LATENCY_RESULTS_2026-09-08.md`.

## Regression coverage

```text
node --test tests/esp8266-small-gzip.test.js tests/esp8266-playlist-web-cache.test.js tests/esp8266-playlist-streaming.test.js
```

The tests compile the actual C code with undefined-behavior checks, compare
gzip decoding against standard zlib, vary feed boundaries, and exercise
writer failure, same-size source edits, corrupted/truncated cache recovery,
unchanged-file reuse, unsupported rows, identity fallback and OFF linking.

Physical upload regression (explicitly opt-in; radio must already be stopped):

```text
node tools/test_esp8266_playlist_gzip_upload.cjs --allow-upload --original <private-full-SPIFFS-backup>/data/playlist.csv --output <report-dir>
```

It changes one station name without changing URLs, validates gzip/identity
equality, repeats an identical upload, then restores the full original in a
finally block. Expect HTTP **303** with `Location: /`, not HTTP 200, after
successful uploads. On restore failure, stop and use the private backup.
Never substitute the filtered HTTP download for the full original CSV;
that would discard unsupported rows. Reports contain hashes and timings,
not Wi-Fi credentials or CSV contents. Three physical checks passed and
the original 53808-byte playlist was restored.
