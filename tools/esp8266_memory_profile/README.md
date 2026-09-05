# ESP8266 production-profile RAM workload

This opt-in test measures the normal native MP3/AAC firmware with Wi-Fi and
I2S PDM active. It does not enable the isolated codec/audio-output benchmarks,
change buffer sizes or add tasks. Never send application commands on UART RX:
GPIO3 is the audio output.

1. Read `/api/native/status` and WebSocket `getindex=1` / `getsystem=1` first.
   Record station, volume, playing state and current application slot. Keep an
   exact ordinary `app.bin` for restoration. Do not alter PC Wi-Fi.
2. Configure `YORADIO_ESP8266_MEMORY_PROFILE=ON`, with audio stage profiling,
   heap tracing and isolated benchmarks OFF. Save the built image under
   `firmware/development/esp8266-native-memory-profile/` with its manifest.
3. Flash only the active application slot. Never rewrite NVS, SPIFFS, partition
   table or OTA selection data for this test. The current two-slot layout is
   documented in `docs/ESP8266_OTA_LAYOUT.md`.
4. Capture TX using `tools/monitor_esp8266.py` throughout the workload. Its
   `--reset` flag pulses RTS; it sends no UART application data.
5. Set `NODE_PATH` to an installed Playwright package location, then run:

   ```text
   node tools/esp8266_memory_profile/run.cjs --host 192.168.100.6 --restore-station 498 --restore-volume 254 --restore-playing false
   ```

   These restoration values are examples: use the actual pre-test state.
   Check the station indices against the board's playlist first. The script's
   test stations 498/502/2/510 refer to the filtered 511-entry ESP8266 list.
   Use `--aac-station N` for another verified AAC entry. `--aac-followup`
   replaces the initial MP3 cases with AAC station 1 (nominal 64 kbit/s),
   while retaining switching and the two-tab workload.
   `--reload-during-audio` also reloads a tab during each codec's playback,
   measuring static-resource/bootstrap allocation peaks.
   Labels are nominal rates, NOT proof of the received codec or bitrate.
   Each completed phase records actual HTTP status. Browser phases open two
   real headless Edge pages and log load success, playlist rows and WS frames.
   Failed commands/pages must not be counted as successful stress coverage.
6. The script closes its own browser and restores station, volume and playback
   in `finally`, but also verify the final status. Then close the UART monitor,
   restore the exact ordinary firmware, reset and verify HTTP/state again.

## Interpreting UART `memory:` records

- `dram_total`: total registered 8-bit-capable heap-region span, not the chip's
  entire physical RAM and not the heap currently available to applications.
- `free`: current free DRAM; `low`: sum of SDK region lifetime low-water marks.
  Region minima need not have occurred simultaneously; resets start a new run.
- `largest`: largest user payload allocatable in one untraced, aligned DRAM
  block at that instant, excluding its heap header. No allocation is attempted.
- `window_free` / `window_largest`: minima sampled by the existing app loop
  since the previous 10-second report. Transients between samples can be missed;
  `low` is the allocator's lifetime measurement, not a sampled approximation.
- `iram_free`: free 32-bit-only heap, separately from byte-addressable DRAM.
  Reserved codec IRAM is already allocated, not spare capacity to add to DRAM.
- `stack_*`: lifetime untouched stack bytes for app/audio/httpd/idle. These
  bytes are inside already allocated stacks, NOT additional free heap. SDK
  Wi-Fi, timer and TCP/IP stack high-water marks are not measured by this mode.
- `valid=0`: invalid heap chain; discard its largest-block result and investigate.

The heap walker uses the SDK's own block flags, links and malloc lock. It logs
only after unlocking, does not allocate memory, and does not enable FreeRTOS
trace arrays. It adds 24 bytes of explicit counters/handles (alignment can make
the linked heap difference 32 bytes). Its periodic report uses the existing
main stack, so that stack's measured margin includes diagnostic overhead.

The first exploratory image also logged `scan_us`; discard that column.
The SDK timer sometimes stepped backwards and underflowed the unsigned delta.
The final memory-only profiler omits timing rather than interpreting it as
interrupt latency or CPU load. Heap and stack counters are unaffected.

Run regressions with `node --test tests/esp8266-memory-profile.test.js`.
