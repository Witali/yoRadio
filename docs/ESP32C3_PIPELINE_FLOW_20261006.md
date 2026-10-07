# ESP32-C3: decoder waits and DMA service delays

## Result

The physical measurements support **delayed DMA servicing during long LPC32
decode calls** as the main explanation of these files' playback shortfall.
The decoder does wait for compressed input and free PCM space, but those waits
do not explain why LPC32 falls behind LPC12 on these two recordings:

- LPC32 spent **less** time waiting for either input or free PCM space.
- The output task almost always found PCM ready, yet the I2S completion queue
  overran **208 and 300 times** in approximately 45 measured seconds.
- LPC32 produced only **95.19% and 93.07%** of real-time audio, despite average
  total CPU loads of **77.51% and 80.40%**.
- Deliberately slowing the source produced a different pattern: **56.48%**
  decoder input-wait time, **412** input timeouts and **60.17%** output-empty
  wait time. This confirms the counters can detect input starvation.

This diagnoses the pipeline; it does **not** fix scheduling or prove the exact
number of audible gaps. No acoustic capture or GPIO scheduling trace was taken.
The new flag is diagnostic and **off by default**. Input/output timeouts,
task priorities, queue sizes, codec arithmetic and DMA configuration are unchanged.

## What the timeouts mean

| Operation | Existing maximum wait | Actual wake-up condition |
|---|---:|---|
| Decoder receives compressed packet | 20 ms | Packet becomes available |
| Decoder reserves PCM queue item | 250 ms | Enough ring-buffer space becomes available |
| Output receives PCM queue item | 5 ms | PCM packet becomes available |
| Output receives completed DMA descriptor | 1000 ms | I2S completion queue has a descriptor |

These are blocking API deadlines, not polling periods and not required delays.
A packet/space becoming available wakes the waiting task early; the scheduler
then decides when it can run. On input timeout the decoder checks its state and
waits again. On PCM timeout it checks generation cancellation and retries.
Increasing the first two values would not create input data or service DMA
sooner; it can delay observing Stop/station changes. **The 20 ms value remains
unchanged, as requested.**

A measured wait can exceed the API deadline because it includes time before
the task actually resumes. It does not mean FreeRTOS deliberately waited that
long before making the task runnable.

## Instrumentation

Enable `CONFIG_YORADIO_PIPELINE_PROFILE=y` together with
`CONFIG_YORADIO_DIRECT_DMA_PCM=y`. The latter is still experimental.

- `PERF FLOW_DEC`: input-empty and PCM-full events, elapsed microseconds,
  maximum wait and timeout counts, with codec and stream generation.
- `PERF FLOW_OUT`: PCM-empty waits, total submission wall time, waits for
  completed DMA blocks, and completion-queue overruns.
- A zero-time receive/acquire first proves the queue was unavailable. Only
  then is the original blocking call timed, with its original deadline.
  Immediate successful operations are not counted as waits.
- Counters are task-local except an aligned monotonic `uint32_t` written by
  the I2S ISR and read by the output task. The C3 callback is **18 bytes in
  IRAM**, has no calls, and only increments an internal SRAM counter.
  No ISR logging, allocation, clock read or atomic helper is introduced.
- The pinned ESP-IDF 6.0.2 driver allocates a completion queue of
  `dma_desc_num - 1` entries. When it is full, the ISR discards the oldest
  completion and invokes `on_send_q_ovf`. We count that event. It is not a
  bit-exact measurement of missing PCM or an acoustic dropout count.
- Normal builds compile back to the original blocking calls and omit profile
  fields/counters. An ELF check confirmed diagnostic symbols are absent in
  the off image.

All reported waits are **wall time including preemption**, not CPU execution
time or a precise trace of the FreeRTOS Blocked state. Decoder and output
windows overlap. DMA wait is also included in submission time. **Do not add
these percentages together as CPU load.**

## Physical method and measurements

Same ESP32-C3 SuperMini OLED, 160 MHz, flash DIO 80 MHz, awake build, direct DMA,
four 512-frame stereo descriptors at 48 kHz, three-block startup prefill.
The files are the original matched 24-bit/44.1 kHz/stereo Groove Salad and
Indie Pop Rocks! captures from the [radio FLAC study](ESP32C3_FLAC_RADIO_20261006.md).
Max LPC order 32 is allowed, not forced; LPC12 remains an LPC control.

Each ordinary case ran for 60 seconds from the start of the same file. LAN
HTTP `/file` uses unpaced writes and TCP backpressure. WebUI polling keeps a
0.1-second delay between requests. Pair order was Groove12, Groove32,
Indie32, Indie12. The separate `/jitter` control used Groove12 for 40 seconds:
average-byte pacing at 1.02x plus 35 ms per 8192 bytes deliberately undersupplies
this high-bitrate file; it is not a simulation of every real Wi-Fi outage.

The first ten seconds and partial windows are excluded. Each normal case has
nine complete decoder and nine output windows, about 45 seconds per task.
The control has five of each, about 25 seconds. No flow logs were malformed.

| File / max LPC order | Mean total CPU | Audio / wall time | Decoder input wait | Decoder PCM-full wait | Output PCM-empty wait | DMA completion overruns |
|---|---:|---:|---:|---:|---:|---:|
| Groove / 12 | 73.43% | 1.0013 | 4.91% | 66.05% | 0.06% | 1 / 45.06 s |
| Groove / 32 | 77.51% | 0.9519 | 2.77% | 58.93% | 0.08% | 208 / 45.07 s |
| Indie / 12 | 77.91% | 0.9964 | 11.51% | 58.15% | 2.16% | 22 / 45.09 s |
| Indie / 32 | 80.40% | 0.9307 | 8.17% | 54.38% | 0.09% | 300 / 45.08 s |
| Groove / 12, input-starvation control | 57.88% | 0.6016 | 56.48% | 25.42% | 60.17% | 937 / 25.03 s |

Zero decoder input timeouts, zero PCM reservation timeouts and zero DMA
acquisition timeouts occurred in the complete ordinary windows. Input waits
there lasted at most 18.883 ms. Full PCM waits averaged 7.12–7.80 ms and peaked
at 27.716 ms. Normal backpressure occupies much of the decoder's wall time:
decoded samples must ultimately play at the hardware sample rate.

| File / max LPC order | Longest FLAC call | Mean timed DMA acquisition | Longest timed DMA acquisition |
|---|---:|---:|---:|
| Groove / 12 | 35.858 ms | 11.086 ms | 42.448 ms |
| Groove / 32 | 47.440 ms | 12.631 ms | 53.322 ms |
| Indie / 12 | 37.107 ms | 11.320 ms | 45.694 ms |
| Indie / 32 | 49.020 ms | 13.032 ms | 56.647 ms |

One DMA block lasts 10.667 ms; four contain 42.667 ms. Task priorities are
decoder **7**, output **6**, stream **5**. Returning a consumed PCM lease can
wake the higher-priority decoder immediately, before the output task fills
another DMA block. The long call durations, ready PCM and completion overruns
are consistent with that scheduling explanation. They do not prove each
individual overrun's cause without a scheduler trace.

No complete CPU window reached 99.9%; the highest ordinary CPU window was
81.5%. Average spare CPU therefore does not guarantee timely DMA service.

## Validation and retained failures

- OTA into the diagnostic image and back to the off image both passed while
  AAC played. Firmware identity and partition changed as expected; Wi-Fi,
  playlist and settings equality checks passed.
- Queue wrapper tests passed with the flag on and off under ASan/UBSan:
  immediate availability, blocking success, timeout, returned ownership,
  original deadlines, absent off-mode stats and 64-bit accumulation.
- Staged output, ordinary DMA and profiled DMA produced identical **12,331,776
  PCM bytes** and identical case metadata under ASan/UBSan. The separate
  normalizer chunk test passed 648 cases with zero added LSB error.
- Both physical configurations built successfully. Profile on adds 2,224
  app bytes, 18 IRAM bytes and 24 BSS bytes in these linked images; aligned
  `.dram0.data` size is unchanged. Task-local counters use existing stacks.
- Parser tests cover duration weighting, incomplete windows, malformed data
  and observed zero waits. Missing telemetry is not converted into zero.
- The first profiled Groove12 load test **failed** its progressive-free-heap
  gate: the first/last three CPU samples' median free heap fell from 65,940
  to 62,440 bytes, while the largest block stayed at 47,104 bytes. Its audio
  timing still passed. The other three profiled load cases
  passed the existing gates. The full original outcome is retained.
- Profiled runtime checks and the starvation-control check passed. A load
  PASS allows audio/wall above 0.9 and therefore **does not certify gap-free
  playback**. The diagnostic build is not production-qualified.

### Profile-off control and final board state

After a second successful OTA, the same source with profiling disabled ran
Groove32 then Groove12 for 60 seconds each. The only on/off configuration
difference is `CONFIG_YORADIO_PIPELINE_PROFILE`. Settled idle heap was measured
for 12 seconds before and after each case.

| Groove variant | CPU with profile | CPU without profile | Audio/wall with profile | Audio/wall without profile |
|---|---:|---:|---:|---:|
| LPC12 | 73.43% | 74.25% | 1.0013 | 1.0003 |
| LPC32 | 77.51% | 78.65% | 0.9519 | 0.9556 |

Both off-image load cases, both idle baselines, both Stop recovery checks and
the final reboot/identity check passed. No `FLOW` logs were emitted with the
flag off. The LPC32 shortfall therefore persists without instrumentation.
The small on/off timing differences are not a calibrated overhead estimate:
these are separate Wi-Fi runs and the second pair had additional idle settling.
The first heap failure did not recur here, but that does not prove its cause
or remove it from the record.

Recorded stack headroom remained at least 13,252 bytes for the decoder and
1,008 for output in the profile run, versus 13,340 and 1,228 in the off run.
These are observed minima, not an all-codec worst-case proof. Minimum recorded
RSSI was -71 dBm with profiling and -70 dBm without it.

The board was left on `firmware/development/esp32c3-pipeline-profile-off/app.bin`,
awake with profiling disabled. Both saved artifacts remain development images;
this investigation does not promote the experimental direct-DMA implementation.

## Reproduce

Use an awake build with the exact same settings as the baseline except the
new flag. Preserve successful images under `firmware/development/`. Do not
install this diagnostic image on a different board.

```powershell
python tools/codec_benchmark/run_pipeline_profile_host.py --output .build/flow/host-profile
python tools/codec_benchmark/run_output_dma_host.py --profile --output .build/flow/host-dma-profile
python tests/test-pipeline-flow.py

python tools/esp32c3_tests/pipeline_flow_study.py `
  --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 `
  --firmware firmware/development/esp32c3-pipeline-profile/app.bin `
  --fixtures .build/radio-flac-20261006/recordings/manifest.json `
  --case radio-groovesalad-lpc12 --case radio-groovesalad-lpc32 `
  --case radio-indiepop-lpc32 --case radio-indiepop-lpc12 `
  --seconds 60 --output .build/flow/board

python tools/esp32c3_tests/pipeline_flow.py --results .build/flow/board --output .build/flow/summary.json
python tests/test-pipeline-flow-evidence.py
```

The hardware runner requires the exact installed image; it does not flash.
Use the existing `diagnostic.py ota_transition` workflow for an intentional
image change. The fixture server and its pacing modes remain board-independent.

Retained results: [evidence directory](../tests/results/esp32c3-pipeline-flow-20261006/),
including hashes, filtered logs, status samples, original failures, exact
sources, build configurations and driver source. Radio audio stays in the
ignored local capture directory. Neither credentials nor raw UART logs are
part of this evidence.

## Next scheduling experiment

The subsequent [output-priority experiment](ESP32C3_OUTPUT_PRIORITY_20261006.md)
implements and measures the first comparison below. The measurements and
board state above describe the original diagnostic run.

1. Compare output-first scheduling or bounded cooperative decode work with
   the unchanged four DMA buffers. Keep decoder **task CPU** separate from
   elapsed decode-call time, which naturally includes output preemption.
2. Require fewer completion overruns and real-time audio on the same LPC32
   files; repeat all-codec PCM, EOF, Stop/switch, OTA and load checks.
3. Measure any throughput cost on MP3, AAC, Vorbis and FLAC before changing
   a default. Increasing queue timeouts is not the proposed remedy.

No scheduling change is applied by this investigation.
