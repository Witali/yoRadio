# Quiet production candidate with runtime health, 2026-10-10

The next production candidate combines the measured early-MPI repair, the
17,058-byte RX-only TLS reserve, adaptive input with four minimum packet slots,
250/500 ms input prefill, four extra FLAC slots and nominal fractional
48 kHz output. It retains ESP-IDF `9a97f6c54ec6`, QIO 80 MHz, full compact
AAC/SBR/PS at native rates and output/decoder priorities 8/7.

The exact image has normal public trust roots, no laboratory CA, no deep
sleep, no console/logging and no optional profiler task or DMA/heap/TCP
probes. Direct-DMA PCM, software integer-rate compensation and FIR are off.
New [on-demand health](ESP32C3_PRODUCTION_HEALTH.md) makes its actual heap,
restarts and lifetime allocation/watchdog counters observable.

`CONFIG_YORADIO_INPUT_MIN_BLOCKS=5` counts 1,600-byte configuration units,
not packet slots: 8,000 requested bytes round up to four 2,060-byte slots
(2,048 audio bytes plus a 12-byte encoded-packet header each). This requests
8,240 bytes of slot storage, excluding allocator and queue metadata. Four
optional FLAC slots bring the limit to eight, subject to the saved target
and heap check. The earlier wording "five minimum slots" was incorrect;
the firmware configuration is unchanged.

## Build evidence

- Version: `idf61-quiet-mpi-health`.
- Application: **1,455,360 bytes**, 656 bytes larger than `quiet-frac4`.
- App SHA-256: `5505393d2b7d4fcad1303b3b96d9c41709c86a84e687bcbeb059a4241d243da6`.
- ELF SHA-256: `6524f1457d6009ee1c229e86bc64a2ff3361fd7df3810b1d2b652b9f0c2ce751`.
- All **119 nonempty code/constant sections in 18 AAC/FLAC objects** are
  byte-identical to the quiet control; full-AAC, HTTP and allocator audits pass.
- Normal trust bundle SHA-256 remains
  `a60bf79ef8943cdcb3d9cc8889a35c7b411fe0136132e79b855742e2eb52dc6d`.
- The only active sdkconfig change against `quiet-frac4` is early MPI-lock
  initialization. Frozen sources additionally include the health endpoint.
- Both quiet fault callbacks reside in IRAM (30 and 16 bytes). Their total
  46-byte text increase fits inside the pre-existing IRAM-end padding.
  Initialized DRAM and BSS each increase by 8 bytes; the heap-start padding
  section increases by 8 bytes. Boot identity plus counters hold 16 bytes.
- Host tests cover absent/malformed telemetry, reboot/fault rejection and
  privacy filtering. Actual callback/handler C passes ASan/UBSan with the
  watchdog enabled and disabled, including maximum-width JSON values.

Build artifacts are under
`firmware/development/esp32c3-idf-6.1-r9a97-quiet-mpi-health/`.
The frozen source/ELF checks exclude the unrelated CLZ experiment.

## Qualification scope

The runner `tools/esp32c3_tests/quiet_acceptance.py` tests format/EOF, AAC
transitions, network recovery and settled memory through the exact quiet
image. Each status sample has a separate health request; its timing includes
both requests. Public AAC is checked with FFprobe plus the independent,
unquantized FAAD PS probe. No broadcast audio or private settings are retained.

Health counters do not measure DMA underruns, PCM accuracy, analog output or
every decoder/TLS error. Passing these checks must not be described as an
acoustic-continuity measurement. Previous instrumented results remain separate
evidence. Long-playback, exact-image HTTPS coverage for every supported codec,
certificate-error behavior and the intermittent TCP timeout remain required
until explicitly verified. Defaults are unchanged during qualification.

## Real HTTPS stations: two retained failures

Five public SomaFM streams each play for 60 seconds using the ordinary public
trust bundle. Original results are **8/10 checks passed**. Independent format
checks pass for every stream. Across 551 health observations, boot identity is
unchanged and allocation-failure/task-watchdog counters remain zero. This is
not a claim that the two failing acceptance cases passed.

| Stream | Independently checked format | Minimum steady free / largest, B | Longest status + health, ms | Original case |
| --- | --- | ---: | ---: | --- |
| 128 kbit/s AAC | LC, 44.1 kHz stereo | 55,788 / 43,008 | 809 | PASS |
| 64 kbit/s AAC | HE-AAC, 44.1 kHz stereo | 20,996 / 8,192 | 7,029 | FAIL: response time |
| 32 kbit/s AAC | HE-AAC, 44.1 kHz stereo | 20,936 / 8,704 | 181 | PASS |
| 16 kbit/s AAC | HE-AAC, 32 kHz mono source, duplicated stereo PCM | 21,152 / 7,936 | 175 | FAIL: contiguous headroom |
| 256 kbit/s MP3 | 44.1 kHz stereo | 79,356 / 63,488 | 200 | PASS |

FAAD reports no PS frames in these particular public captures; they do not
qualify real-stream HE-AACv2. The local HE-AACv2 fixture is separate evidence.
After Stop, settled median free heap is 139,904 B versus 140,128 B initially;
largest capacity stays 114,688 B and task count stays 16. Recovery passes.
The SDK's lifetime minimum free heap reaches 13,816 B; that includes transient
startup/handshake allocations and differs from the sampled steady-state minima.

### Slow response attribution

The 7,029 ms paired observation occurs about 12 seconds into HE-AAC playback.
The health request itself takes 6,770 ms. Host transport request 258 spends
1,772 ms connecting and 4,997 ms waiting for response headers; its body read
takes less than 1 ms. All 1,120 connection attempts eventually succeed.

The device includes its own uptime at snapshot construction. Intersecting
nearby fast request intervals, allowing 10 ms for timestamp granularity and
local clock drift, places **4.907..4.980 seconds after that snapshot**. Heap
inspection occurs before the timestamp in the handler, so a long heap walk
cannot explain this portion. This narrows the investigation to sending,
transport or host reception after handler computation; it does not identify
the lost packet or establish Wi-Fi as the cause. PktMon driver status queries
are denied by Windows even outside the sandbox; no capture was started and
no monitoring filters were changed.

### Headroom failure

The mono-source HE-AAC case briefly has a largest block of **7,936 B**, 256 B
below the existing 8,192 B steady-state budget. Current free memory remains
above 21 KiB in that case's steady samples and the allocation counter remains
zero. Preserve this as a headroom failure, distinguish it from an actual OOM,
and compare required allocation sizes/lifetimes before changing the budget
or input-pool policy. Neither this threshold nor the response-time threshold
was relaxed.

## Next public HTTPS fixtures

FFmpeg's public collections provide candidates for
[FLAC](https://samples.ffmpeg.org/A-codecs/lossless/),
[Opus](https://samples.ffmpeg.org/A-codecs/opus/) and
[Vorbis](https://samples.ffmpeg.org/ogg/Vorbis/).
These are discovered sources, not completed tests. Verify their codec, rate,
channels, bit depth, duration and TLS connection before board acceptance.

## Completed local and OTA qualification

The independent local campaign completes **42/42** checks.
The cases cover MP3, FLAC, Vorbis, Opus, AAC-LC, HE-AAC and HE-AACv2
files with automatic and explicit codec selection, EOF, AAC transitions,
Stop/Play generation, connection drop/stall/error, redirect/jitter,
WebSocket format/reconnect, settled recovery and lifetime health.

| Phase | Passed / total | Original failures |
| --- | ---: | --- |
| Public HTTPS | 8 / 10 | https:groovesalad-64-aac; https:groovesalad-16-aac |
| Local HTTP / lifecycle | 42 / 42 | None |
| OTA | 13 / 13 | None |

Settled local observations, in bytes:

| Checkpoint | Median free heap | Median largest block | Tasks |
| --- | ---: | ---: | ---: |
| initial | 140,120 | 114,688 | 16 |
| http | 139,936 | 114,688 | 16 |
| transitions | 139,936 | 114,688 | 16 |
| network | 139,936 | 114,688 | 16 |
| websocket | 139,936 | 114,688 | 16 |

All 1,071 local health observations retain the same boot ID,
with 0 allocation failures and 0 task-watchdog events.
The sampled minimum current free heap is 25,308 B;
minimum largest block is 13,312 B. These are
sampled current values, not the SDK lifetime low-water mark.

The OTA suite includes invalid uploads, interrupted/stalled uploads,
two accepted application updates and reboot/settings verification.
OTA while playing and slow valid uploads are not part of this run.

Both controllers restore `idf61-listen48-8c1f2d`, verify the exact ELF
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`,
confirm settings persistence and record three stopped observations.
No serial recovery is used. The candidate remains **not production-qualified**.

Byte-exact evidence, all failed cases and offline replay instructions:
[qualification archive](../tests/results/esp32c3-quiet-health-20261010/README.md).
