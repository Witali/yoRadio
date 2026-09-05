# ESP8266 native: physical RAM headroom audit, 2026-09-05

## Scope and method

Physical Wemos D1 mini, CPU 160 MHz, QIO 40 MHz, SDK v3.4 / GCC 8.4 / O3,
native Helix MP3 SSO + AAC, GPIO3 ordinary I2S PDM32 with 2 x 512-word DMA.
Display disabled; normalizer disabled as found on the board. The KaRadio
producer remains OFF. No audio buffer or stack sizes were changed.
The active codec input buffer is 1536 bytes; PCM storage is 2304 bytes for MP3
and 4096 bytes for AAC. Unused legacy board constants are not allocated RAM.

An opt-in memory-only build samples the actual SDK allocator from the existing
application loop and reports every ten seconds. It uses no extra task or trial
allocations. Explicit diagnostic state is 24 bytes in the final image; linker
alignment reduces the DRAM heap by 32 bytes compared with the ordinary build.
Stack margins include diagnostic reporting on the existing main stack.

The first run used an earlier 28-byte-counter image with an extra `scan_us`
column. That column is invalid when the SDK clock regresses and must be ignored.
It was removed for the independent AAC run. RAM measurements do not depend on
that timer. Both images preserve the same audio, Wi-Fi and WebUI configuration.

The linked diagnostic DRAM budget is 98,304 bytes: 20,880 bytes for static
sections/alignment, followed by a 77,424-byte heap region. Free stack space is
inside allocated stacks; it must NOT be added to free heap. Free 32-bit-only
IRAM was 0 or 24 bytes in the first run; the reserved 16-KiB codec arena is
already in use, not additional free DRAM.

## Measurements

All values below are bytes. `low` is the allocator's lifetime low-water mark
since the most recent reset. Largest-block minima are sampled, not allocation
trace minima: sub-sample transients can be missed. Only one DRAM heap region
exists in this SDK configuration.

| Workload | Representative free DRAM | Lifetime low | Smallest sampled largest block |
| --- | ---: | ---: | ---: |
| Stopped, before audio, final profile | 24,856 | 21,708 | 21,376 |
| MP3 128, no loaded pages, first run | 10,120–12,696 | 7,816 | 7,428 |
| AAC 320, no loaded pages, second run | 13,256–14,204 | 9,084 | 8,852 |
| AAC -> MP3 -> AAC switching, second run | 12,860–14,196 after AAC restart | 8,336 | 8,336 |
| MP3 128 with two loaded pages | 2,652 after collapse | 1,160 | **548** |
| AAC 320 with two pages, after one page reload | 12,780–13,072 | 5,136 | 5,108 |
| MP3 128 with two pages, independent repeat | 2,152 after collapse | 1,472 | **548** |

The second nominally 256-kbit/s MP3 preset (Europe Plus) actually decoded at
128 kbit/s. This run does NOT certify MP3 256/320-kbit/s headroom. AAC Opera
was confirmed through WebSocket as `AAC 320 kbps 44 kHz stereo`, so its result
is not based solely on an `icy-br` header. A brief read-only WS format query
also ran during that otherwise page-free AAC interval.

## Failures are part of the result

- Both real headless Edge pages loaded all 511 playlist rows (2.300 / 2.014 s
  in the first run). However, WS sessions reconnected intermittently.
- Starting MP3 with two pages drove `free` down to a sampled 1,468 bytes and
  the allocator lifetime minimum to 1,160 bytes. Largest payload fell to 548
  bytes. WS payload sends failed and subsequent status/control requests timed
  out. Closing the browser did not restore service within the test's three
  cleanup retries; a reset was required.
- The current station remained ROCK FM during failed control attempts. The
  later nominal two-tab AAC phase in that first run never started AAC and is
  NOT counted as AAC coverage.
- Station 507 (Radio Rodnykh Dorog) failed HTTP stream opening, so it was
  replaced in the follow-up workload by existing playlist entries 1 and 2.
- AAC station 1 decoded near 63 kbit/s, then failed output with
  `PCM output failed: ESP_ERR_TIMEOUT` / decoder result `-7`. Its heap minimum
  was 10,164 bytes. Do not classify this observed output timeout as proven OOM
  or claim continuous low-bitrate AAC playback passed.
- AAC 320 had a clean remote stream EOF and successfully reconnected. This is
  a memory audit, not certification of uninterrupted audio or network quality.
- In the independent AAC run both pages again loaded 511 rows (1.928 / 2.362 s).
  Reloading one page during AAC completed in about 18.5 s and status recovered
  with HTTP 200 / 26 ms. Memory fell to a lifetime minimum of 5,136 bytes;
  the sampled largest block was 5,108 bytes. There were WS reconnects and a
  `WS frame is not properly masked` warning, so do not call this protocol-stable.
- The independent final-profile run reproduced the MP3 failure after the AAC
  tests: `low=1472`, `window_largest=548`, failed WS sends and HTTP timeouts.
  The test runner/its own headless browser and UART monitor were explicitly
  stopped after this reproduction instead of waiting for more failed requests.
  Its `finally` cleanup did not complete; restoration was done and verified
  separately below. Do not interpret the truncated second JSONL as a pass.

## Stack margins from the first run

| Task | Allocated stack | Minimum untouched bytes |
| --- | ---: | ---: |
| Application main | 3,072 | 1,576 |
| Audio | 4,096 | 1,360 |
| HTTP/WebUI | 5,120 | 2,292 |
| Idle | 1,024 | 792 |

No exhaustion of these measured task stacks was observed. Wi-Fi, TCP/IP,
SDK timers and ISR-stack high-water marks were not instrumented: enabling
all-task tracing would change the memory configuration. OTA/upload paths were
not exercised, so this does NOT justify reducing the production 5-KiB HTTP
stack. The diagnostic's main-stack overhead also makes it unsuitable as a
precise estimate of spare bytes that can be removed from that task.

## Decision

Do not increase the default compressed buffer or enable the additional network
reader yet. Even an extra 1 KiB is not supported by the observed worst case.
The remaining producer ring (4 KiB) plus its 2.5-KiB stack, URL and task control
storage would exceed the available reserve by several times.

Prioritize bounded WebSocket/TCP backpressure and resource release under
disconnect/slow-client conditions, then repeat these measurements. The data
shows a memory collapse correlated with WS failures, but does not yet identify
every retained allocation or prove a particular leak. Keep the separate AAC
PCM-output timeout and a controlled MP3 320 test on the follow-up list.

## Reproduction

Use `tools/esp8266_memory_profile/README.md` and the saved script. Test images
and hashes are described in
`firmware/development/esp8266-native-memory-profile/manifest.md`.
The script restores original settings in `finally`; when the firmware cannot
accept commands, recovery must be verified after reset/ordinary-image restore.
The pre-test state was station 498 ROCK FM, volume 254, playback stopped,
smart-start setting 2. Wi-Fi and PC network configuration were not changed.

## Saved evidence and restoration

- [Clean UART logs, workload JSONL and summary](benchmarks/esp8266-memory-2026-09-05/).
  There are 75 first-run and 47 second-run RAM snapshots; all have `valid=1`.
  ANSI color escapes and unrelated Wi-Fi/boot identifiers were removed from
  the public UART excerpts. Private unfiltered captures stay under `.build/`.
- All 330 repository tests passed; the four memory-profile regressions were
  repeated successfully after the final workload edits. Profile ON and OFF
  configurations compiled. The local CMake cache was returned to memory
  profiling OFF; the measured ELF/map remain in ignored build storage.
- The exact ordinary 688640-byte app was flashed back to app0 (0x10000), with
  esptool hash verification and an RTS reset. No NVS/SPIFFS/OTA-data writes.
  SHA-256: `76E47B98D18CCC7C259FCFDDE7A627D1266C6A6D17A408E103F4C9BD3BABAE59`.
- Post-restore status: client Wi-Fi, no error, stopped, ROCK FM, free heap
  24,632 bytes, lifetime minimum 21,752 bytes, app address 65,536. WS confirmed
  station 498, volume 254, smart-start 2 and normalization disabled, matching
  the pre-test state. No `memory:` instrumentation runs in the restored image.

The buffer-growth acceptance item remains open because the stress test found
failures. Its measurement subitems are completed; do not convert observed
spare stack bytes or an idle heap snapshot into a new buffer default.
