# ESP32-C3 public radio HTTP/HTTPS checks — 2026-10-01

## Outcome

**Full HE-AAC radio playback is not qualified.** The fixed TCP-pool image
passes AAC-LC and MP3 HTTPS playback with frequent WebUI requests, but real
HE-AAC/HE-AACv2 streams still fail the 55,128-byte SBR allocation and continue
with reduced AAC-core PCM. HTTP comparisons under the same polling load also
fail that allocation. With lighter HTTP polling, full SBR starts, but smaller
allocations fail during playback. TLS adds pressure, but is not the only
remaining obstacle.

The subsequent [dynamic TLS-buffer experiment](ESP32C3_TLS_DYNAMIC_20261001.md)
recovers roughly 18–21 KiB in the passing LC/MP3 HTTPS observations while
preserving record capacity and certificate verification. Public HE/v2 still
fail the SBR allocation; this is an optional follow-up, not a change to the
image or historical results below.

This extends the [passing local HTTP/OTA checks](ESP32C3_LWIP_HALF_CLOSE_20261001.md).
It does not invalidate those recorded results or qualify streams they did not
exercise. The firmware, decoder arithmetic, settings and TLS configuration
were unchanged throughout this experiment.

## Image and method

- Physical C3, CPU 160 MHz, DIO 80 MHz, no PSRAM; deep sleep and Flash Auto
  Suspend off. Full Espressif AAC/SBR/PS, optional RTC TCP pool and ownership fix.
- Installed app: `firmware/development/esp32c3-tcp-pcb-pool-fixed/app.bin`.
  ELF SHA-256: `7b9414f9d153c1762d250755267c6ab5bf3603991ad0bbf4379262d94466dae3`.
  App SHA-256: `2da9c04a2a34df7892e36be44d676e067a5896774fac69cf9c4f6f16c8f030d9`.
- Each stream observed for 60 seconds. A REST request is followed by a 100 ms
  delay; this produces about 5.5 requests/second, not a claimed 10 Hz request
  rate. Successful cases also require matching WebSocket state, CPU/heap
  budgets and real-time decoding progress. Passive USB capture detects faults.
- The public URLs come from [SomaFM's direct links](https://somafm.com/groovesalad/directstreamlinks.html).
  Its [FAQ](https://somafm.com/about/faq.html) identifies the advertised AAC
  encodings. FFprobe 8.1.1 with `-tls_verify 1` independently probes the live
  profile/rate/channels immediately before each case. No broadcast audio or
  title metadata is retained. Encodings/music can change between runs.
- HTTP uses the same server and path. A separate
  [host check](../tests/results/esp32c3-public-https-20261001/host-http-check.json)
  confirms HTTP 200 without an HTTPS redirect for the comparison endpoints.
  This is not a recommendation to downgrade production radio URLs.
- The installed TLS configuration keeps RX 16 KiB, TX 4 KiB and certificate
  bundle verification. No test CA or verification bypass was added.

## Measured comparison

The table uses FreeRTOS samples **5–35 seconds after the first decoded-frame
checkpoint**, consistently with earlier memory surveys. The full acceptance
runner separately checks its stable 15–60 second window. Values are observed
runtime RAM/CPU, not isolated allocator costs. Every row is stereo unless it
explicitly says mono; output samples are 16-bit.

| Public input / reference | Transport | Result and observed PCM | Mean total / decode CPU | Minimum free / largest RAM, bytes |
| --- | --- | --- | ---: | ---: |
| AAC-LC 128 kbit/s, 44.1 kHz | HTTPS | PASS: 44.1 kHz | 52.983% / 20.850% | 32100 / 17408 |
| AAC-LC 128 kbit/s, 44.1 kHz | HTTP | PASS: 44.1 kHz | 49.540% / 20.500% | 62912 / 51200 |
| HE-AAC 64 kbit/s, 44.1 kHz | HTTPS | **FAIL: core 22.05 kHz** | 36.783% / 10.633%* | 30376 / 18432 |
| HE-AAC 64 kbit/s, 44.1 kHz | HTTP | **FAIL: core 22.05 kHz** | 34.500% / 10.040%* | 61304 / 49152 |
| HE-AAC 32 kbit/s, 44.1 kHz | HTTPS | **FAIL: core 22.05 kHz** | 34.217% / 9.550%* | 30552 / 14848 |
| HE-AACv2 16 kbit/s, 32 kHz | HTTPS | **FAIL: core 16 kHz mono** | 26.600% / 4.733%* | 28972 / 17408 |
| HE-AACv2 16 kbit/s, 32 kHz | HTTP | **FAIL: core 16 kHz mono** | 25.940% / 4.580%* | 54428 / 40960 |
| MP3 256 kbit/s, 44.1 kHz | HTTPS | PASS: 44.1 kHz | 65.483% / 26.800% | 60644 / 45056 |
| MP3 256 kbit/s, 44.1 kHz | HTTP | PASS: 44.1 kHz | 57.533% / 26.150% | 86256 / 69632 |
| HE-AAC 64 kbit/s, 44.1 kHz | HTTP, 1 s polling | **FAIL: full 44.1 kHz, later allocation errors** | 50.560% / 34.020% | 6232 / 1728 |

\* CPU for failed rows measures **core-only fallback**, not full HE-AAC; it
cannot be used as a full-decoder performance result or optimization gain.

AAC-LC's sampled free RAM is about 30.1 KiB lower over HTTPS; MP3's is about
25.0 KiB lower. These are sequential live workload differences, including
network buffers and allocator placement, not a precise fixed TLS allocation.
Passing HTTPS cases have maximum sampled REST latencies of 281 ms (LC) and
297 ms (MP3), below the existing two-second budget.

## Allocation failure and recovery

Every row below is the actual failed request for **55,128 contiguous bytes**:

| Transport / input | Total free, bytes | Largest block, bytes | Diagnosis at that instant |
| --- | ---: | ---: | --- |
| HTTPS / HE 64 | 39892 | 29696 | Total RAM deficit and fragmentation |
| HTTPS / HE 32 | 39964 | 28672 | Total RAM deficit and fragmentation |
| HTTPS / HEv2 16 | 41888 | 29696 | Total RAM deficit and fragmentation |
| HTTP / HE 64 | 60236 | 53248 | Total exceeds request; no large enough block |
| HTTP / HEv2 16 | 60376 | 53248 | Total exceeds request; no large enough block |

Even a successful SBR allocation must leave room for its 1,180-byte control
object, networking, WebUI and the published minimum heap budget. Merely making
the largest block slightly bigger is not sufficient production qualification.

There were no retained panics, heap corruption reports, capture interruptions
or unexpected resets. Each run has one deliberate final software reboot to
restore the saved station. Wi-Fi, playlist and settings compare equal in RAM.
The HTTPS idle samples recover to 145768–145788 free bytes, largest block
114688, 17 tasks, versus about 145800 before the run.

The initial HTTPS runner at `9b0748f4` reports `idle:recovery` as FAIL because
its final health check also sees the already recorded SBR allocation failures.
That entry is retained unchanged; it is not evidence of an idle heap leak.
The updated runner at `4b975e92` keeps allocation failures in their playback
cases and checks heap recovery/reboots separately. The HTTP recovery check passes.

### Lighter HTTP polling

A separate 60-second HE 64 kbit/s test after a reboot uses a one-second delay
between REST requests. It produces full `HE-AAC 44.1 kHz stereo`, but fails
the allocation/heap gate: **61 requests for 1,700 bytes and one for 1,512 bytes**
fail with only about 3.3–5.2 KiB total free and blocks as small as 1,216 bytes. The failure hook
does not identify the owning subsystem, so these are not conclusively assigned
to Wi-Fi, TCP or HTTP. No SBR allocation fails in this run.

This distinguishes two failure modes: allocating the large SBR object, and
retaining enough working memory after it succeeds. The differing polling rate
and fresh playback sequence can affect allocation timing; this is not a clean
proof that polling alone caused the earlier SBR failures. Heap recovery and
settings restoration pass again.

## Reproduce and retained evidence

See the [test instructions](ESP32C3_TESTING.md#https). With an awake profiling
image already installed:

```powershell
python tests/test-esp32c3-public-streams.py
python tools/esp32c3_tests/public_streams.py --board http://BOARD_IP --serial-port COM9 --firmware firmware/development/esp32c3-tcp-pcb-pool-fixed/app.bin --seconds 60 --interval 0.1 --output .build/public-https
python tools/esp32c3_tests/public_streams.py --board http://BOARD_IP --serial-port COM9 --firmware firmware/development/esp32c3-tcp-pcb-pool-fixed/app.bin --seconds 60 --interval 0.1 --transport http --case groovesalad-128-aac --case groovesalad-64-aac --case groovesalad-16-aac --case groovesalad-256-mp3 --output .build/public-http
python tools/esp32c3_tests/summarize_public_windows.py --input .build/public-https --output .build/public-https/summary.json
```

Reports preserve expected failures, reference probes, exact image/config/test
hashes, sanitized status samples, serial performance logs and settings equality:

- [HTTPS report](../tests/results/esp32c3-public-https-20261001/load/report.json),
  [summary](../tests/results/esp32c3-public-https-20261001/load/summary.json).
- [HTTP comparison](../tests/results/esp32c3-public-https-20261001/http-comparison/report.json),
  [summary](../tests/results/esp32c3-public-https-20261001/http-comparison/summary.json).
- [HTTP with one-second polling](../tests/results/esp32c3-public-https-20261001/http-light/report.json),
  [summary](../tests/results/esp32c3-public-https-20261001/http-light/summary.json).
  Reproduce with `--transport http --case groovesalad-64-aac --interval 1`.

## Next acceptance work

1. Trace surviving allocations around the real HTTP SBR failure; the RTC pool
   removed the earlier TIME_WAIT obstruction but not every cause of fragmentation.
2. Reduce the simultaneous decoder/transport budget with measured lifetimes.
   Preserve full SBR/PS, both channels, rates, TLS receive capability and the
   user's buffer range. Early reservation alone does not save RAM.
3. Re-run these streams and the controlled HTTP/HTTPS matrices, switching,
   CPU/heap, one-hour soaks and OTA after each accepted change. Keep this image
   experimental. No Auto Suspend or lossy AAC change is justified by these tests.

These are short live network checks. They do not establish acoustic quality,
stereo separation, waveform accuracy, worst-case interrupt latency, or support
for every legal AAC tool/transition. The controlled HTTPS fixture matrix still
needs a trusted fixture origin.
