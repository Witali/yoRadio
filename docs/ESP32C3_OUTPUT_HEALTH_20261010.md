# Quiet output health qualification

## Production observability

The staged PDM output exposes two lifetime `uint32_t` counters in the additive
`output` object of `/api/native/health` (schema 1):

- `completion_queue_drops`: the I2S driver discarded a completion notification
  before the output task consumed it. This indicates delayed service; it is
  **not an acoustic gap count**.
- `write_errors`: an attempted I2S write returned an error or accepted fewer
  bytes than requested. One failed attempt increments this counter once.

`available=true` means the staged backend implements these measurements.
The experimental direct-DMA backend returns `available=false`; zero counters
there must not qualify output continuity. Older schema-1 images without the
object remain readable for heap/watchdog checks but cannot pass output checks.

Only the overflow callback increments the queue counter. Only the output task
increments the write counter. Neither counter is reset by Stop/Play. Reads
are aligned words on the single-core C3; the two counters are not one atomic
snapshot. Differences use modulo-2^32 arithmetic, with boot identity and
uptime checked separately. Startup, idle and Stop can contribute queue events:
compare only explicitly selected sustained-play windows.

The new persistent state is two 32-bit words. There is no new task, allocation,
logging, timer read or per-completion callback; the interrupt callback runs only
when the existing driver reports queue overflow. The HTTP stack response buffer
grows from 384 to 512 bytes. Final placement/size must be checked in the ELF.

## Host verification

Run from the repository root with Python; the native tests use GCC via WSL on
Windows:

```text
python -B tests/test-production-health.py
python -B tests/test-production-health-native.py
python -B tools/codec_benchmark/run_output_dma_host.py --profile --output <new-result-directory>
```

The actual C handler is checked at maximum-width values with watchdog enabled
and disabled, using AddressSanitizer and UndefinedBehaviorSanitizer. Actual
output C is exercised for callback registration failure, ISR counter wrap,
successful/short/failed writes, and persistence across suspend/reinitialize.
The staged and direct backends, with and without profiling, retain identical
PCM and case metadata (432 rate/channel/volume/balance/normalization cases per
variant). Host tests do not establish physical interrupt timing.

The Python reader rejects malformed counters, filters unknown fields, accepts
older basic-health responses, and rejects absent/unavailable output telemetry
for output measurements. Window deltas exclude historical events and handle
counter wrap; reboots and zero-duration windows fail closed.

## Completed build and physical qualification

The saved candidate is
`firmware/development/esp32c3-idf-6.1-r9a97-quiet-output-health/app.bin`,
app SHA-256 `ada20228227e7fc6af79de6ba01d26b4da2b98b140a1faca4ab9c398f53df99d`,
ELF SHA-256 `322c5db5d8c903185e0464b64662fb4b3092bd76d5e3cdca0ff58d3251425964`.
It retains the previous quiet image's entire sdkconfig: QIO/80 MHz, awake,
nominal 48 kHz fractional clock, public trust roots, full compact AAC and
the existing TLS/input reserve policy. It has no optional runtime profiler.

The 18-byte overflow ISR is a leaf function in IRAM: load, increment, store
and return, with no calls. Its code fits existing section padding. Persistent
DRAM grows by 8 bytes. All 119 audited AAC/FLAC code/constant sections in 18
objects match the previous candidate. Comparing all 50 application objects,
only output and WebUI change; 48 objects retain identical code/constants.

The physical public HTTPS HE-AAC 64 kbit/s test completes **7/8 checks**:

| Measurement | Result |
| --- | --- |
| Requested playback observation | 600 seconds; first PCM at 2.45 s |
| Independently checked format | HE-AAC, 44.1 kHz stereo, no PS in reference |
| Sustained output window, excluding 15 s startup | 584.019 s, 507 paired samples |
| Completion-queue drops / write errors in that window | **0 / 0** |
| Lifetime allocation failures / watchdog events | **0 / 0**, one boot identity, 540 health samples |
| Minimum sampled free heap / largest block | **20,684 / 7,424 B** |
| SDK lifetime minimum free heap, including transients | 12,920 B |
| Longest combined status + health response | 200.19 ms |
| RSSI range | -83 to -67 dBm |
| Idle median free heap, before / after | 139,968 / 139,716 B |
| Idle largest block / task count, before and after | 114,688 B / 16 |

The sole failure is the unchanged contiguous-memory headroom gate: at 76.475 s
one sample has a largest block of 7,424 B, below the 8,192 B budget, while total
free heap is 24,668 B. This is **not an observed allocation failure**. There
are no output-counter events around it. Startup/idle queue events are retained
in the raw lifetime counters and excluded only from the sustained-play delta.

Format, output, response time, complete collection, memory recovery, settings
and lifetime health pass. The historical seven-second WebUI delay did not recur
in this test; one successful run does not establish its cause or resolution.

The controller restores the exact listened `idf61-listen48-8c1f2d` image
(ELF `76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`),
verifies Wi-Fi/playlist/settings persistence and three stopped observations.
It exits with failure to retain the failed memory gate. An offline replay
reproduces all measured verdicts and verifies restoration.

## Remaining work

Investigate required allocation sizes and lifetimes under TLS, including valid
AAC frame growth, before changing input reserves or accepting a lower headroom
budget. The candidate remains **not production-qualified**. These counters
do not prove analog continuity or universal station compatibility, and this
long-playback run covers one public HE-AAC stream.

[Raw evidence, frozen sources and offline replay](../tests/results/esp32c3-output-health-20261010/README.md).
