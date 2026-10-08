# ESP32-C3 HTTP/TLS/AES receive-path measurements

Date: 2026-10-08. ESP-IDF 6.1 revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`.

## Purpose and scope

The heavy HTTPS FLAC case still saturates the CPU and misses timely DMA
service. The [tick comparison](ESP32C3_FREERTOS_TICK_20261008.md) did not fix it,
and the [optional GHASH experiment](ESP32C3_GHASH_EXPERIMENT_20261008.md) did not
improve physical playback. Measure the receive path before choosing another
optimization. Keep 1 ms ticks, output/decode/stream priorities 8/7/5, normal
GHASH, the same buffers, full-rate compact AAC and all original failure gates.

`CONFIG_YORADIO_TLS_PATH_PROFILE` is disabled by default. Its overlay adds fixed
counters and linker wrappers, with no extra task, heap allocation, payload
capture or changes to crypto results. Only calls made by `radio_stream` count.
The existing HTTP CPU profiler prints snapshots at most every five seconds.

| Stage | Measured call | Meaning of bytes |
| --- | --- | --- |
| HTTP | `esp_http_client_read` in `stream_http_read` | Requested capacity / returned body bytes |
| TLS | SDK-wrapped `mbedtls_ssl_read` | Requested capacity / returned authenticated bytes |
| poll | `esp_transport_poll_read` | Zero; readiness checks have no byte request |
| GCM | `esp_aes_gcm_auth_decrypt` | Ciphertext length / length on successful authentication |
| CTR | `esp_aes_crypt_ctr` | Requested length / length on success; includes GCM tag encryption |

These are **inclusive wall times**, including preemption and blocking, not
per-function CPU times. HTTP contains transport/TLS, GCM contains CTR, and
calls may cross snapshot boundaries. Do not add their percentages, or label
their differences exact CPU costs. Whole-task CPU measurements are recorded
separately. Counters are charged on return; the maximum call time is cumulative
since boot, not the maximum of a selected playback window. Size bins describe
requested lengths, and poll always occupies the zero-byte/<=1024 bin.

The TLS wrapper preserves the SDK dynamic receive-buffer adapter and the
radio's distinction between raw EOF and a TLS closure alert. HTTP still
preserves already authenticated partial bytes and closes a fatally failed
connection before queue backpressure can block the caller.

## Hardware AES on this board

`CONFIG_MBEDTLS_HARDWARE_AES=y` and `CONFIG_SOC_AES_SUPPORT_DMA=y` are enabled.
ESP32-C3 accelerates AES-128 and AES-256. In the pinned SDK's partial GCM path,
CTR uses hardware AES; GHASH is software in `port/aes/esp_aes_gcm.c`. Hardware
AES therefore does not eliminate the CPU work of TLS record authentication,
HTTP parsing, copying, allocation and peripheral setup.

`CONFIG_MBEDTLS_AES_USE_INTERRUPT=y` is also enabled. In
`port/aes/dma/esp_aes_dma_core.c`, `AES_DMA_INTR_TRIG_LEN` is 2000 bytes: longer
DMA operations can wait on a semaphore; smaller operations use busy waiting.
Small-data block-mode optimization is another driver branch; request sizes
alone do not prove every internal DMA operation's size. Do not attribute the
entire CTR duration to busy waiting without measuring the selected path.

## Verification and reproduction

- `tests/test-tls-path-profile.py`: actual wrappers/counters under ASan/UBSan;
  nested timings, unchanged arguments/results/output mutations, failures,
  retries/EOF, task isolation, size-bin boundaries and 64-bit time counters.
  Underlying crypto, clock, locks and task API are scripted in this host test.
- `tests/test-stream-http-reader.py`: real SDK HTTP parser/read functions and
  the radio's error guard with diagnostics disabled; retains 85 framing/error
  cases. This is not a full cryptography or scheduler test.
- `tools/esp32c3_tests/verify_tls_path_link.py`: actual RISC-V caller/callee
  routes into each wrapper and back to the real implementation.
- `verify_http_link.py`: separately checks the preserved SDK dynamic-RX chain.
- `tests/test-tls-path-summary.py`: valid deltas and rejection of incomplete,
  duplicate, malformed, reset or interrupted telemetry.
- `tools/esp32c3_tests/tls_path.py`: replays recorded `performance.json` and
  `status.json`, excluding the first ten playback seconds. Requires at least
  three complete snapshots and reports coverage gaps separately from results.

Run the host tests with the IDF Python and WSL GCC, then build with the existing
CPU-profile HTTP and staged-DMA overlays plus `sdkconfig.tls-path-profile.defaults`.
The saved controller runs only HTTPS FLAC 48 kHz stereo/16-bit for 60 seconds
and alternating-record HE-AACv2 44.1 kHz stereo for 90 seconds. Native OTA
installs the diagnostic image; a `finally` block restores the quiet image and
checks unchanged settings and playback state. No acoustic capture is made.

## Physical measurements

The FLAC receive-path window contains ten complete snapshots, covering
45.628992 seconds between the first and last device timestamps. No HTTP retry,
zero-byte read, poll timeout, GCM authentication failure or CTR error was
recorded in this selected window.

| Stage | Completed calls | Inclusive wall time / observed time | Mean elapsed time per call |
| --- | ---: | ---: | ---: |
| HTTP | 3,293 | 76.656% | 10,621.80 us |
| TLS | 6,585 | 66.782% | 4,627.46 us |
| Socket readiness | 6,585 | 2.238% | 155.06 us |
| GCM authentication/decryption | 6,586 | 30.581% | 2,118.74 us |
| AES-CTR | 13,172 | 6.014% | 208.35 us |

All GCM payload calls in this window are 1024 bytes: 6,744,064 authenticated
bytes / 6,586 calls. CTR has two calls per GCM operation, with an additional
16-byte tag block per record. One-call differences between nested stages are
expected at snapshot boundaries. This establishes use of the instrumented
hardware AES path; it does not convert those durations into CPU attribution.

There is no evidence of an `EAGAIN` retry spin in this FLAC window. Most TLS
wall time is outside CTR; even GCM duration alone does not account for all TLS
time. Candidates for further measurement are record reception, PSA/context
setup, buffer management and GHASH. The previous byte-GHASH implementation did
not improve playback; retain that negative result when choosing experiments.

| Image / case | Mean CPU busy | Decoded audio / wall time | DMA queue overruns / observed time | New watchdog events |
| --- | ---: | ---: | ---: | ---: |
| Earlier diagnostic baseline / FLAC | 100.00% | 0.965882 | 154 / 45.109 s | 11 |
| TLS-path diagnostics / FLAC | 99.14% | 0.921306 | 339 / 45.110 s | 10 |
| Earlier diagnostic baseline / HE-AACv2 | 74.76% | 1.001584 | 0 / 75.110 s | 0 |
| TLS-path diagnostics / first HE-AACv2 run | 67.26% | 1.001558 | 0 / 75.110 s | 0 |
| TLS-path diagnostics / repeated HE-AACv2 | 67.00% | 1.001464 | 0 / 75.109 s | 0 |

The FLAC runtime gate still **fails**, and measured output is worse with this
diagnostic image. Profiling changes instruction placement and adds overhead;
this is not a production optimization or a nonintrusive cost measurement.
There is only one FLAC run per image. RF conditions also vary (median/minimum
RSSI -60/-71 dBm for this FLAC run versus -61/-61 dBm previously). Do not claim
a causal AAC speedup from the lower CPU number. No SDK output-write or captured
allocation errors occurred in these two runs. Minimum unused stack observed:
radio stream 1,860 B; HTTP server 3,984 B in FLAC and 3,952 B in AAC.

The first AAC run passes the original playback/runtime and idle-memory gates,
but its new TLS profiling capture **fails** validation: snapshot 27 is missing
the HTTP and TLS rows inside the playback window. Its aggregate TLS-path
measurement is unavailable. Preserve that failure and repeat only AAC, without
relaxing the parser. A DMA queue overrun denotes a dropped completion
notification, not a measured number of audible gaps or lost samples.

### Repeated AAC measurement

The repeat has 16 complete snapshots over 75.830531 device seconds, with no
coverage gap. Original playback/runtime and idle-recovery gates pass again.

| Stage | Completed calls | Inclusive wall time / observed time | Mean elapsed time per call |
| --- | ---: | ---: | ---: |
| HTTP | 191 | 29.093% | 115,505.68 us |
| TLS | 174 | 1.612% | 7,026.39 us |
| Socket readiness | 227 | 27.297% | 91,185.43 us |
| GCM authentication/decryption | 36 | 0.625% | 13,173.31 us |
| AES-CTR | 72 | 0.062% | 654.85 us |

GCM processes 18 records of 1024 bytes and 18 records of 16384 bytes. All
authenticate successfully. There are 35 HTTP `EAGAIN` returns and 53 poll
timeouts across this window; they accompany substantial socket waiting,
not a high-rate busy retry loop. No retry delay change is justified by this
measurement. HTTP's cumulative duration is dominated by readiness polling;
hardware AES is a very small part of elapsed playback time for this AAC case.
Stream-task CPU is 0.44%, while decode-task CPU is 42.89%.

The repeat records zero DMA overruns, watchdog events, SDK write errors and
allocation-failure rows. Minimum free heap/largest block is 25,800/17,408 B;
median/minimum RSSI is -61/-73 dBm. Stream/HTTP minimum unused stack is
2,528/3,996 B. Unlike the first AAC run, this follows a reboot without a preceding
FLAC test, so the lifetime stack watermark must not be interpreted as a smaller
per-call stack requirement. Neither short AAC run qualifies long-term memory
stability or acoustic continuity.

## Saved image

The diagnostic image is under
`firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-tlspath/`:

- Embedded version: `idf61-9a97-tlspath`.
- ELF SHA-256: `5aee16bafd5d2c2817456563aaea44db7dab2254648d839a4a233d62c8db7e85`.
- Application SHA-256: `f7f65bd761af4ac043258012db10d5f44b6a44cda3ae8bdcd8f841d97c6a91f8`.
- Application size: 1,620,384 bytes.
- Only sdkconfig difference versus the diagnostic baseline:
  `CONFIG_YORADIO_TLS_PATH_PROFILE=y`. Embedded build labels differ.

Linked section changes: IRAM and initialized DRAM unchanged; `.dram0.bss`
+320 B, flash code +1,976 B and flash read-only data +272 B. The application
image grows by 2,256 B. These are diagnostic costs, not production savings.

This remains a laboratory-only, **NOT_QUALIFIED** image, with the test CA added
to the ordinary root bundle and certificate validation enabled. It does not
supersede the retained [long AAC heap-trend failures](ESP32C3_TLS_RX_RESERVE_20261008.md).
Keep the profiler disabled and hardware AES enabled in normal builds.

Both native-OTA installations and restorations passed. The final quiet image
has ELF SHA-256 `da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0`;
Wi-Fi, playlist and settings are unchanged, and three status samples over
15 seconds confirm resumed AAC playback. The pinned SDK working tree is clean.

Raw runs, the rejected initial AAC profile, host-test reports, final linked
audit, build logs, source snapshots and SHA-256 index are retained in
[`tests/results/esp32c3-tls-path-20261008`](../tests/results/esp32c3-tls-path-20261008).
The initial build lacked an explicit `tcp_transport` header dependency; the
corrected build passes. The initial link audit expected uninlined counter
calls; the final audit retains and checks compiler-generated `.part.0` and
inline counter bodies. These audit/build failures are preserved separately
from physical playback failures. Host checks: 46 native integration tests,
four telemetry-summary tests, wrapper sanitizer tests and 85 HTTP cases pass.
