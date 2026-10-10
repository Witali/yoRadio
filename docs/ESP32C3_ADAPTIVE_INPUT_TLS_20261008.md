# Adaptive compressed-input storage for TLS

This ESP-IDF 6.1 experiment lets mbedTLS reclaim **idle** compressed-audio
packet slots above a configured minimum. It remains disabled by default.
It does not compact the heap or guarantee a full-sized TLS allocation.

The later [static TLS reserve experiment](ESP32C3_TLS_RESERVE_20261008.md)
can be combined with this queue. In that combination only, input capacity is
reduced at startup and remains at its minimum to fund the permanent reserve.
The adaptive-only behavior and historical measurements below remain separate.

## Configuration and capacity

Use `sdkconfig.adaptive-input.defaults` with the C3 native build, or set:

```ini
CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=y
CONFIG_YORADIO_INPUT_MIN_BLOCKS=5
```

The minimum uses the existing 1,600-byte settings unit. Both target and minimum
round up to complete slots; the minimum is capped by the configured target.
The current slot contains a 12-byte packet header and up to 2,048 audio bytes.
The existing NVS setting is unchanged. With the default target of 10 units:

| Storage | Slots | Allocated packet bytes |
| --- | ---: | ---: |
| Target | 8 | 16,480 |
| Minimum | 4 | 8,240 |
| Maximum reclaimable, if idle | 4 | 8,240 |

Queue control, two semaphores and allocator metadata are additional overhead.
Each short packet still occupies a full slot; this differs from the original
variable-sized ring and can reduce effective buffering for fragmented reads.
The WebUI fill percentage describes occupied slots divided by resident slots.
The ordinary configuration continues to use its existing ring and fill metric.

## Ownership and allocation order

- A slot moves through idle, producer-owned, queued and decoder-owned states.
  Only idle slots can be freed. Queued compressed bytes, EOF markers and
  producer/decoder pointers remain intact and in FIFO order.
- Before each mbedTLS allocation, compare the largest free internal byte-addressable
  block with the request. Reclaim idle slots until the request fits or no
  eligible slot remains. A raced allocation failure can reclaim another idle
  slot and retry; an unrecoverable failure still reaches the SDK normally.
- Never wait for the decoder from the TLS allocation callback. A completely
  occupied queue cannot help that allocation immediately. The original heap
  failure logs are not suppressed, including a failure recovered on retry.
- In adaptive-only mode, restore absent slots between connections, after the old HTTP/TLS client is
  closed. Do not regrow storage during playback and repeatedly compete with TLS.
- The wrapper intercepts `esp_mbedtls_mem_calloc` in internal-memory mode.
  Its matching frees remain unchanged. It is not a general heap allocator and
  does not intercept direct allocations in ESP-IDF crypto/network drivers.

Queue state changes are protected by a critical section. Heap operations and
semaphore operations happen outside that section. Every wait keeps its original
deadline, including stale semaphore notifications and tick-counter wrap.
Full 16 KiB incoming TLS records, certificate verification, AAC LC/SBR/PS,
codec precision and sample rates are unchanged.

## Validation

The target is pinned ESP-IDF revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`.

- The actual queue and TLS wrapper pass ASan/UBSan host tests, including 30,000
  concurrent producer/consumer packets with reclamation, allocation failures
  at every constructor stage, leases, FIFO order, minimum capacity, failed
  restoration, tick wrap, multiplication overflow, successful TLS reclaim,
  raced allocation failure and fragmented frees that cannot satisfy TLS.
- The actual stream task passes 37 connection/retry/EOF tests with the feature
  enabled and 37 with it disabled. The enabled harness checks restoration is
  performed only after the previous HTTP/TLS client is destroyed.
- The firmware builds; full-AAC and HTTP link checks pass. A separate ELF audit
  verifies that `mbedtls_calloc_func` points to the new wrapper, and that the
  wrapper calls the original allocator, largest-block query and slot reclamation.

These host tests simulate heap layout and RTOS events; they are not physical
TLS, audio continuity or PCM-quality measurements. The changed audio service
also compiles against the ordinary quiet configuration with the feature off;
that is a compile-only check, not a new full-image qualification.

Reproduce the host checks:

```powershell
python tests/run-adaptive-input.py --output .build/adaptive-input-host
python tests/run-stream-connection-retry.py --adaptive-input --output .build/adaptive-stream-host
```

On Windows the host runners use GCC in WSL. Use fresh output directories.

## Physical result: reservation reclaimed, contiguous TLS request still fails

The saved [laboratory image](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-adaptive/manifest.json)
has ELF hash `e2c3e0d5c4880547cf371751d3b1252aed68d14d3b0d0233998d02a1f678299c`.
It uses the same RX6/dynamic-TLS configuration as the latest-SDK control,
static Wi-Fi RX/BA settings of six, full compact AAC and an extra laboratory
CA alongside normal public roots. It is not a production-qualified image.

Both 75-second observation windows alternate 1 KiB and 16 KiB application
records containing HE-AAC v2 at 44.1 kHz stereo. Both reach full PCM format,
then fail the 16,749-byte TLS allocation. This is roughly five seconds of
playback before failure, **not** 75 seconds of successful playback.

| Run | First full PCM | Allocation failure | Free heap then | Largest block then | Terminal status |
| --- | ---: | ---: | ---: | ---: | ---: |
| Initial capture | 0.813 s | 4.938 s | 34,400 B | 15,360 B | 5.516 s |
| Repeated capture | 0.781 s | 4.953 s | 33,920 B | 12,288 B | 5.406 s |

The original capture filter did not retain the new counter line. A narrow
numeric-only filter and its regression test were added, then the same image
was tested again. The repeated capture records:

```text
TLS_INPUT released=4 retries=0 request=16749 resident=4 minimum=4 target=8 occupied=0 capacity=8240
```

Thus four idle slots (8,240 allocated packet bytes) were actually freed before
the failing allocator call, with the minimum intact. The heap still lacked a
large enough contiguous block. The reported free-byte totals are heap
observations, not a matched estimate of this feature's net RAM saving. RSSI
varied from -82/-83 to -59 dBm; these runs do not isolate RF or CPU performance.

Idle recovery and settings verification pass in both runs. Each controller
restores the ordinary awake firmware by application-only OTA, verifies its
ELF hash, unchanged Wi-Fi/playlist/settings and playback in three observations
over 15 seconds. No serial flash or reset was needed.

Original failed reports, host checks, build/link evidence and measured sources
are retained in [the evidence archive](../tests/results/esp32c3-adaptive-input-20261008/).
Private TLS keys and captured broadcast audio are excluded. The allocator
feature remains off by default; the board is back on the ordinary firmware.

## Remaining acceptance gates

The same full-record HE-AAC test that fails with ordinary dynamic TLS must pass,
followed by ten-minute playback, all codec/HTTP/HTTPS cases, Stop/Play/EOF,
network faults, high-bitrate buffering and OTA. Measure actual reclaimed heap
and the largest block, not just the nominal slot sizes. Packet integrity alone
does not demonstrate freedom from physical audio underruns.
The ten-minute and full-codec matrix were not repeated for this rejected memory
configuration. Combine or compare it with a separately reserved full RX block
before treating it as a solution to the TLS fragmentation problem.
