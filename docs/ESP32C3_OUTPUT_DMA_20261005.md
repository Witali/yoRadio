# ESP32-C3 PCM buffering and direct DMA experiment

Date: 2026-10-05. Native C3 firmware; no changes to CYD/ESP8266 output paths.

## Ownership audit

| Storage | Current role | Decision |
| --- | --- | --- |
| Native AAC caller PCM, 8192 B | Complete HE-AAC stereo frame, then generation-tagged PCM queue | Keep: a codec frame is larger than one DMA block; output processing is still required |
| Other simple-decoder caller PCM, initially 12288 B | Espressif MP3, Ogg/Vorbis, Ogg/Opus and other selected simple decoders write into this caller-owned workspace | Keep the grow/retry contract; do not substitute a 2048-byte DMA block for a full codec frame |
| Optional Helix/minimp3 adapter PCM, 4608 B | Whole MP3/AAC-LC frame passed to callback | Keep for now: larger than the PCM queue's maximum packet; a queue-lease redesign needs separate backend tests |
| Custom FLAC adapter PCM, 2048 B on the decoder stack | Convert segmented channel workspaces into interleaved PCM; mono is compacted in place | Candidate for direct PCM-queue reservation; this experiment does not change that API or reduce the shared Opus-sized task stack |
| PCM ring, 8192 B | Separate decoder/output tasks, backpressure, stream generation and EOF ordering | Keep; deleting it would couple frame decoding to hardware timing |
| Output staging array, 2048 B | Gain/resampling writes a block which `i2s_channel_write` copies again | Removed in the experimental direct-DMA variant |
| Four I2S DMA blocks, 4 × 2048 B | Hardware PCM-to-PDM output, 512 stereo s16 frames/block at 48 kHz | Keep all four: about 10.67 ms/block, 42.67 ms total |
| AAC SBR/QMF, Vorbis overlap/MDCT, Opus state, FLAC channel workspaces | Codec arithmetic/history, not duplicate final PCM | Preserve |

The native AAC adapter's input `memcpy`/`memmove` assembles compressed frames.
Those operations are not PCM output copies. This audit does not claim that all
private instructions of every vendor decoder have been decompiled.

## ESP-IDF 6.1 follow-up, 8 October

The direct-DMA implementation remains optional. Its CMake source-hash guard
still accepts only the audited 6.0.2 I2S implementation. In the pinned 6.1
revision `9a97f6c54ec638111ce55cd36581b3c192f15207`, both driver files differ:
`i2s_common.c` SHA-256 starts `87b3443817bf`, and `i2s_private.h` starts
`49fecb9c0a8a`. Enabling the option currently fails configuration. Audit the
new descriptor ownership, writer locking and lifecycle before changing the
guard; the old physical results are not a 6.1 qualification.

For that comparison, `CONFIG_YORADIO_STAGED_DMA_PROFILE=y` adds diagnostics
to the ordinary staged output. It is disabled by default and mutually
exclusive with direct DMA and QEMU. The unchanged stock `i2s_channel_write`
path, PCM arithmetic, buffer capacities, timeout and task priorities remain.
An optional `on_send_q_ovf` ISR callback only increments an aligned DRAM word;
reporting runs in the output task. A linked 6.1 audit confirms an 18-byte IRAM
callback with no calls, a 4-byte DRAM counter and 32 bytes of task-local
accounting. Registration failures retain the existing channel cleanup path.

The cumulative `PERF STAGED_DMA:` record contains completion-queue overruns,
write attempts, actual written bytes, total/max write wall time and errors.
An SDK error or short write remains an output failure. Silence and startup
ramps also affect these counters: compare deltas only within sustained
playback, after warmup. A queue overrun is delayed service, not an exact
number of missing samples. Write wall time includes waiting and preemption.
The maximum is since boot, not a reconstructed maximum for a selected window.

The host ASan/UBSan comparison passes all 432 PCM cases for staged, direct,
and both instrumented variants, with the same 12,331,776-byte PCM hash shown
below. Normalizer checks pass all 648 settings with zero LSB differences.
Additional fault injection covers failed callback registration, SDK timeout,
short writes and cumulative counter retention. Six parser tests reject
damaged rows/resets and preserve gaps in telemetry coverage. The optional
6.1 image builds and passes linked AAC/HTTP/TLS allocation audits. Its physical
follow-up below retains the failed FLAC qualification.

```text
python tools/codec_benchmark/run_output_dma_host.py --profile --output <new-host-directory>
python tests/test-staged-dma.py
python tools/esp32c3_tests/staged_dma.py --input <completed-playback-study> --output <new-summary.json>
```

The parser retains the original acceptance results and never declares
acoustic continuity qualified. Deltas cover only the first through last
selected samples, without extrapolation. Evidence is retained under
`tests/results/esp32c3-staged-dma-profile-20261008/`; the laboratory build is
`firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof/`.
It includes a test CA and experimental TLS settings and is not a production
default recommendation.

### Physical staged-output baseline

On the pinned 6.1 build above, the 60-second HTTPS FLAC case recorded 154
completion-queue overruns across 45.109 seconds between sustained-playback
samples after warmup (3.414/s). Its runtime gate failed with 11 new watchdog
events. The 90-second HE-AACv2 case with alternating 1/16 KiB TLS records passed
its original gates and recorded zero overruns across 75.110 observed seconds.
Telemetry coverage was complete in both selected windows; SDK write errors
were zero. The 20,490 microsecond maximum write duration was since boot and
carried into the subsequent AAC run; it is not an AAC-specific maximum.

The separate ten-minute FLAC run lagged real time by 2.56% and captured 114
watchdog events. Memory shortage was not observed in that run. These counters
establish delayed DMA service, but no electrical or acoustic capture was made.
The controller restored the quiet image and verified settings and playback.
See the [immutable raw evidence](../tests/results/esp32c3-rxonly-long-20261008/)
and the [matched TLS comparison](ESP32C3_TLS_RX_RESERVE_20261008.md).

## Implementation (final experimental variant)

`CONFIG_YORADIO_DIRECT_DMA_PCM=y` selects `native_audio_output_dma.c`.
The default remains off while timing/continuity qualification is incomplete.
The old implementation remains the explicit A/B control.

The [long-playback RX ownership follow-up](ESP32C3_RX_OWNERSHIP_20261005.md)
records bounded startup packet buffering and post-stop heap recovery on this
prefill design. It retains the initial heap gate failures and an Opus WebUI
latency failure; it does not promote direct DMA to the production default.

The output task normalizes PCM in place in the existing queue, then writes
gain-adjusted, resampled stereo samples directly into the driver's available
DMA region. There is no borrowed DMA pointer in the decoder and no compressed
decoder work in an interrupt. No pointer survives the synchronous fill callback.

`native_i2s_generator.c` uses the real, named private types from ESP-IDF 6.0.2.
It preserves the installed writer's binary semaphore, one-second timeout,
preload queue and stale-pointer checks. Music always acquires a fresh descriptor
and fills all 512 frames in one callback. Only the bias-ramp/bring-up path uses
partial writes. CMake pins both
`i2s_common.c` and `i2s_private.h` by SHA-256; an SDK change requires a new audit.
The SDK checkout itself is unchanged. C3 internal SRAM needs no cache writeback.

The synchronous fill callback must only perform bounded PCM processing. It
must not allocate, wait for networking, decode a compressed frame or retain the
pointer. Moving a whole decoder into that callback would invalidate the timing
assumptions. The [IDF I2S API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/i2s.html)
also exposes ISR callbacks, but they are not used to run a decoder here.

An unavailable DMA block makes the output task wait. The PCM ring absorbs some
delay and then applies backpressure to the decoder. A timeout is an output
failure, not a successful write. Four blocks reduce scheduling risk but cannot
guarantee uninterrupted sound through arbitrary stalls. Queue/CPU tests are
not a substitute for physical sample/IRQ continuity measurements.

## Whole blocks, queue ownership and startup

The first direct-DMA implementation resumed partially filled descriptors across
PCM packet arrivals. Although its arithmetic test passed, the physical HE-AACv2
44.1 kHz run delivered only **0.88326 seconds of audio per wall-clock second**.
The stock driver's stale-buffer check can abandon a partial descriptor after
an input wait. This first candidate is rejected, and its failure is retained.

The final implementation keeps source PCM in the existing 8192-byte ring until
a complete DMA block can be produced. Queue items contain a named lease record;
no new PCM allocation or copy is made. Returned items can wake the decoder, so
release callbacks run only after DMA filling and after releasing the driver
lock. Stop/generation changes and suspend discard pending leases; EOF and rate
changes flush the final block, padding only its unused end with PCM zero.

At stream startup, gather **three blocks / 1536 output frames / 32 ms** before
submitting music. PDM continues outputting silence while gathering; this does
not disable/restart the carrier or rerun the bias ramp. This is a three-block
source prefill followed by consecutive DMA writes, not a claim that physical
DMA is held stopped until a hardware occupancy counter reaches three.
The four descriptors remain **4 × 2048 B**, about **42.67 ms** in total.

The experimental PCM queue packet size is 2048 B instead of 3584 B, so three
stereo blocks and their queue/lease headers fit in the unchanged 8 KiB ring.
EOF can start a shorter file immediately. If the input queue is temporarily
empty for 32 ms after the first pending sample, allow a smaller prefill rather
than deadlocking a short or highly fragmented stream. DMA still receives whole
blocks. This timeout limits only the startup wait, not the lifetime of a DMA
pointer. The normalizer retains its sample-based envelope across packet calls.

## Verified size and PCM results

| Linked section | Staged control | First direct candidate | Final with leases/prefill |
| --- | ---: | ---: | ---: |
| DRAM BSS | 31480 B | 29432 B | **29464 B** |
| DRAM data | 12620 B | 12620 B | 12620 B |
| IRAM text | 43354 B | 43354 B | 43354 B |
| Flash text | 1122010 B | 1121746 B | 1123330 B |

Final static RAM saving: **2016 B**. Lease headers consume space inside the
existing fixed-size PCM ring, not additional heap allocations. They reduce its
usable payload capacity. Codec PCM workspaces, four DMA descriptors and the
8 KiB source ring remain. Full-rate AAC/SBR/PS and compact PC19 settings are
unchanged; deep sleep is disabled in all physical comparison images.

Host ASan/UBSan tests compile the actual old/new output C and DMA helper with
platform/RTOS stubs. **432 cases**, including all nine rates from 8 to 48 kHz,
mono/stereo, volume/balance combinations and irregular chunks, produce identical
PCM: **12331776 bytes**, SHA-256
`5c0536fec9f7e968a8de7e92f868f86032b11c4b4f4ba3304b82804b8f1f0f09`.
Both sides explicitly zero-pad the final partial descriptor for comparison.
The normalizer callback is stubbed in this ownership test; a separate test of
the actual `AudioNormalizer` compares 3584-byte vs 2048-byte packet boundaries
across **648 settings**, with **zero LSB differences**.

Fault checks cover queue timeout, lock failure, stopped channel, stale partial
pointer, release outside the driver lock, malformed sample length, cancellation,
rate change, suspend, three-block startup and startup timeout. They check
software ownership/arithmetic; they cannot certify real DMA interrupt deadlines.

## Physical A/B comparison

Same board, full PC19 decoder settings, no sleep, seven matched fixtures, 40 s
per case under WebUI polling. The first 10 s are excluded from CPU comparison.
Percentages are FreeRTOS task runtime (waiting on DMA is not busy CPU).
All original acceptance failures are retained in the table.

| Codec | Decoder CPU before → after | Output CPU before → after | Decode time per audio second change | Audio / wall ratio after | Load gate before → after |
| --- | ---: | ---: | ---: | ---: | --- |
| AAC-LC 48k | 19.33% → 19.52% | 6.38% → 6.27% | +2.79% | 1.00160 | PASS → PASS |
| HE-AAC 48k | 39.27% → 39.45% | 5.50% → 5.67% | +0.17% | 1.00159 | PASS → PASS |
| HE-AACv2 44.1k | 45.07% → 43.17% | 7.20% → 6.75% | -4.60% | 1.00133 | PASS → PASS |
| Vorbis 48k | 40.43% → 40.82% | 6.15% → 6.25% | +0.59% | 1.00186 | PASS → FAIL |
| Opus 48k | 47.98% → 48.08% | 6.37% → 6.10% | -0.60% | 1.00166 | FAIL → FAIL |
| MP3 48k | 29.78% → 29.92% | 6.22% → 6.32% | -0.11% | 1.00143 | FAIL → FAIL |
| FLAC 48k | 23.47% → 23.47% | 6.07% → 5.95% | +1.13% | 1.00158 | FAIL → PASS |

All final audio/wall ratios are approximately 1.001: the measured 44.1 kHz
slowdown is gone. Combined decoder+output CPU changes by -2.35 to +0.48
percentage points. This short comparison does not establish zero speed change:
decode time per audio second varies from -4.60% to +2.79%. No emulator correction
is used. The rejected first candidate's lower HE-AACv2 CPU was caused by slower
playback and must not be presented as a speedup.

The FAIL entries are the unchanged progressive-heap-loss gate. The staged
control fails for Opus/MP3/FLAC; the final candidate fails for Vorbis/Opus/MP3.
These runs do not identify the owner or prove equivalence of long-term memory
behavior. [Vorbis plan step 4](ESP32C3_VORBIS_REPAIR_PLAN.md) remains open.
The default build therefore keeps `CONFIG_YORADIO_DIRECT_DMA_PCM` disabled.

Three OTA transitions while playing passed, including installation of the
final image; application hash and preserved settings were checked. All four
EOF status checks (Vorbis / HE-AACv2, auto / explicit codec) passed, including
the WebSocket stopped state. After the tests the board rebooted into the final
experimental image and resumed its saved station. There is no physical PCM/PDM logic-analyzer capture
or long soak qualification, so do not infer sample-level continuity or absence
of audible clicks from task/HTTP timing alone.

## Artifacts and reproduction

- `firmware/development/esp32c3-output-staged/`: A/B control with Vorbis retry/EOF repair.
- `firmware/development/esp32c3-output-dma/`: rejected first candidate; retain for comparison only.
- `firmware/development/esp32c3-output-dma-leased/`: intermediate whole-block build, not installed.
- `firmware/development/esp32c3-output-dma-prefill/`: final experimental image used on the board.
- [Retained results](../tests/results/esp32c3-output-dma-20261005/README.md): all PASS/FAIL logs,
  host snapshots, build checks, initial/final comparisons and hashes.

```text
python tools/codec_benchmark/run_output_dma_host.py --output .build/output-dma-host
python tools/esp32c3_tests/compare_output_dma.py --control <control-load> --candidate <prefill-load> --output <comparison.json>
python tests/test-output-dma-evidence.py
```

The retained load report identifies all fixture hashes, exact firmware ELF and
sdkconfig. Use `tools/esp32c3_tests/diagnostic.py run --suite load --load-seconds 40`
with the seven fixture names in that report, board/host/serial arguments and
`--fixture-manifest <stress-fixtures/manifest.json>`. Logs are filtered technical
telemetry; Wi-Fi settings and private station URLs are not retained.
