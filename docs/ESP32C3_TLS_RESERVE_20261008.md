# Full-record TLS reserve and minimum audio input

This optional ESP-IDF 6.1 experiment reserves one contiguous TLS allocation
and trades compressed-input capacity for networking headroom. Both build
options remain **off by default**. Short paced-stream success alone does not
qualify this profile for production.

## Allocation and ownership

`CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE` adds an aligned static-DRAM slot.
Its capacity comes from the pinned SDK's dynamic-buffer definitions, including
the allocation header and the post-handshake retained-RX conversion. With
full 16,384-byte input records it occupies **17,058 bytes**. Incoming record
limits, certificate verification and codec features are unchanged.

The mbedTLS calloc/free hooks use the slot for one qualifying allocation.
It is not tied to an RX call site: a large handshake allocation can also claim
it. Smaller requests, oversized requests and another simultaneous allocation
use the normal SDK allocator. The slot is zeroed before returning it, and its
used bytes are securely erased before another caller can acquire it.
This preserves ordinary pointer ownership; no live allocations move.

The pinned SDK audit covers dynamic RX allocation, cache/retained-buffer
conversion, failure cleanup, context destruction and recovery of the original
allocation base on free. Both allocator function pointers are checked in the
linked ELF. Direct crypto-driver allocations, ESP-TLS context allocations and
Wi-Fi/lwIP buffers are outside this hook. This is **not a reservation of all
memory needed by HTTPS**.

## Funding the reservation before streaming

Combine the following overlays with a separate laboratory build:

```text
sdkconfig.adaptive-input.defaults
sdkconfig.tls-large-reserve.defaults
```

With both options enabled, the adaptive input queue is reduced to its minimum
at startup and does not grow between connections while the static reserve
exists. This applies to HTTP as well as HTTPS: the reserved DRAM remains
occupied regardless of the current URL or TLS record length. The user's NVS
buffer setting is preserved as the target.

For the existing target of 10 units and minimum of 5 units, each unit being
1,600 bytes, the queue changes from eight 2,060-byte packet slots to four:
**8,240 allocated packet bytes are released**. Queue controls, semaphores and
heap metadata are additional overhead. This reduces tolerance for network
jitter; throughput and continuity still require physical qualification.

Only idle slots can be released. Queued data and producer/decoder leases keep
their pointers and FIFO order. `TLS_INPUT request=0` identifies proactive
budgeting, rather than a failed allocation. Without the static reserve, the
[adaptive-only mode](ESP32C3_ADAPTIVE_INPUT_TLS_20261008.md) still reclaims idle
slots on TLS pressure and restores capacity between connections.

## RAM accounting

These measurements use ESP-IDF revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`, full compact PC19 AAC, static Wi-Fi
RX/BA six, dynamic TLS, RX copying and the six-segment TCP receive window.

| Image | IRAM text + DRAM data/BSS | Static SRAM including padding |
| --- | ---: | ---: |
| RX6 dynamic control | 89,000 B | 89,472 B |
| Adaptive input only | 89,024 B | 89,504 B |
| Static reserve, late input reclamation | 106,136 B | 106,608 B |
| Static reserve, startup input minimum | 106,136 B | 106,608 B |

The reserve adds 17,104 bytes of static SRAM including alignment/padding
relative to the adaptive-only image. Releasing 8,240 packet bytes does not
cancel that cost. The IRAM alias section `.dram0.dummy` is excluded to avoid
counting the same physical RAM twice. These are linked layout measurements,
not peak concurrent heap-use measurements.

## Host validation

The actual C allocator and queue code pass ASan/UBSan tests, including:

- 8,000 concurrent large allocation/free operations per pool-only/adaptive
  configuration; alignment, zeroing, fallback, exhaustion and balanced frees.
- 30,000 producer/consumer packets with reclamation; pointer leases, FIFO,
  failure injection, minimum capacity and timeout/tick-wrap behavior.
- Early minimum capacity with the permanent reserve, no regrowth between
  connections, and intact queued/decoder-owned packets during preparation.
- 37 connection/retry/EOF cases with the optional input path and 37 without
  it, including preparation after the old HTTP/TLS client is destroyed.

Reproduce using fresh output directories:

```powershell
python tests/run-tls-large-reserve.py --output .build/tls-reserve-host
python tests/run-adaptive-input.py --output .build/adaptive-input-host
python tests/run-stream-connection-retry.py --adaptive-input --output .build/adaptive-connections
```

The host runners use GCC/ASan/UBSan in WSL on Windows. These tests do not
measure physical networking, output underruns or acoustic audio quality.

## Physical qualification

### Late input reclamation: rejected

Image ELF `04777e1899b83549d05681fe020b0a15aa8384cfcf084afd2c078b3434b1caac`
uses the static slot but still regrows the input queue before each connection.
The full-record allocation succeeds; fast file delivery exposes a different
shortage of smaller networking allocations.

| Physical test | Result | Recorded allocation failures |
| --- | --- | ---: |
| Small / large / growing / alternating TLS records, 75 s each | 4/4 PASS | 0 |
| HTTP framing inside TLS, including orderly and abrupt termination | 0/8 PASS | 67 |
| Eleven fixtures over HTTP/HTTPS, automatic and explicit codec hints | 31/44 PASS | 99 |

The framing cases use 1 KiB TLS records and do not claim the large slot during
that phase. One failure requests 1,512 B with 4,844 B free but only a 1,088-byte
largest block; another requests 1,024 DMA-capable bytes with 3,500 B free and an
800-byte largest block. An input counter reaches six occupied slots out of
seven resident slots, leaving too little idle storage to reclaim immediately.

The alternating-record run reaches full 44.1 kHz stereo HE-AAC v2 in 0.922 s.
Its observed mean/peak CPU load is 62.52%/67.1%, with 18 pool allocations and
18 releases by idle, no busy fallback and no oversized request. The decoded
audio/wall-time ratio is 1.0021. These are short-run software measurements,
not acoustic proof of uninterrupted output or a ten-minute qualification.

Both controllers restore the ordinary awake image by application-only OTA,
verify its ELF hash, unchanged Wi-Fi/playlist/settings, and saved-station
playback in three observations over 15 seconds. Private keys and captured
broadcast audio are excluded from the evidence archive.

### Startup minimum: follow-up

Image ELF `16c3ee996b66323787627d9e6ff07073e11dfef1936519f5ae43df3945d01c04`
funds the permanent TLS slot before packets arrive and prevents input regrowth.
All eight framing cases now pass, with zero captured allocation failures.
The three 75-second large/growing/alternating record cases also pass, with
full 44.1 kHz stereo HE-AAC v2 and no runtime faults. At idle the pool reports
49 allocations and 49 releases, with no busy fallback or oversized request.

The small-record case remains a recorded failure: its status polling raises
`URLError -> TimeoutError` after 45.704 seconds. The last successful response
at 40.594 seconds still reports HE-AAC v2 playback; observed RSSI spans
-84 to -59 dBm. No memory/decoder/TLS fault is captured in that suite. The
timeout's cause is not established, and weak RF alone is not proof of cause.
The controller restores ordinary firmware and verifies settings and playback.

| Passing record case | Mean / peak CPU | Minimum observed free heap | Minimum observed largest block |
| --- | ---: | ---: | ---: |
| Large | 67.57% / 69.0% | 26,240 B | 15,360 B |
| Growing | 67.59% / 70.0% | 17,848 B | 6,656 B |
| Alternating | 67.27% / 69.0% | 25,736 B | 16,384 B |

CPU is informational, without an 85% acceptance limit. These observations do
not isolate allocator overhead from RF, cache layout or run-to-run variation.
The extended matrix passes **43/44 file cases**, with **zero captured allocation
failures**: HTTP 22/22 and HTTPS 21/22. All AAC variants pass. The remaining
`https:flac-level8:auto` case fails the unchanged runtime-diagnostic gate;
explicit FLAC selection passes.

That failure contains `MEPC=0x420823b2`, `RA=0x42082458` and
`MCAUSE=0xdeadc0de`. Address resolution against the exact ELF maps both code
addresses to `ip4_input` in the pinned lwIP `ip4.c` (lines 835 and 787).
The SDK defines `0xDEADC0DE` as a software-written invalid cause used for
register dumps without a crash. A nearby CPU window records 99.7% busy, but
the watchdog reason line was not captured. Thus this is a retained diagnostic
failure consistent with a nonfatal watchdog dump, **not proof of an allocation
failure, CPU exception or reboot**. Testing continues to subsequent cases.
The suite does not fail merely for exceeding a CPU percentage budget.

The transport-timed small-record repeat passes all 75 seconds, including
runtime, heap recovery and settings checks. There are no transport failures;
the maximum measured connect/header/body phases are 156/125/219 ms (separate
requests, not additive). It observes 379 full-format samples, mean/peak CPU
65.25%/70.3%, minimum free heap 26,064 B and minimum largest block 18,432 B.
The original timeout remains unresolved and retained; neither timeouts nor
retry behavior changed. All three follow-up controllers restore the ordinary
awake image and verify unchanged settings and playback.

The ten-minute run is skipped after the matrix failure; it is not counted as
passing or blocked.
Results of the two images remain separate; a failed run is not replaced by
a later success. Production qualification remains open until the full codec,
TLS framing/record-size, ten-minute playback, reconnect and OTA gates pass.

## Follow-up work

The [further memory research priorities](ESP32C3_MEMORY_STABILITY_TODO.md#further-memory-research-priorities)
track RX-owned reuse for small and large TLS records, bounded packet pools,
decoder lifetime reuse and operating headroom for networking, crypto and WebUI.

- Reproduce the FLAC diagnostic with the timeout reason and task names retained
  safely. Check scheduling and actual output continuity; keep the original
  diagnostic failure and do not replace it with a CPU-budget exemption.
- Classify the small-record WebUI timeout using request-phase timing without
  increasing timeouts or adding hidden retries. The instrumented 75-second
  repeat passes; a failed-request phase trace has not yet been captured.
- Consider a separate RX-specific reservation path for small records as well
  as full records. The current generic pool deliberately rejects requests below
  16,384 B, so it occupies DRAM while small dynamic RX buffers still use heap.
  Audit `esp_mbedtls_add_rx_buffer`, its matching frees, cached state, setup/reset
  and concurrent contexts before changing that policy. Do not let small,
  long-lived handshake/context allocations capture the entire slot.
- After short gates pass, run ten-minute playback, public stations,
  high-depth FLAC/LPC32, negative certificate tests, reconnect/network faults
  and repeated OTA/load checks. No acoustic or DMA-underrun qualification is
  claimed by the status/heap measurements here.

## Saved artifacts

The [evidence archive](../tests/results/esp32c3-tls-reserve-20261008/) contains
original successful/failed reports, transport timings, source snapshots and
hashes, build/link checks, allocator tests and the FLAC address-resolution
command/result. The tested [late-reclamation image](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve/manifest.json)
and [startup-minimum image](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-floor/manifest.json)
remain labelled laboratory-only and not qualified for production.
