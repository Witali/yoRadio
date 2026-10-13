# Shared decoder arena: FLAC DMA investigation

## What the original failure does and does not show

The 100 KiB private arena trial on October 12 recorded **31 new I2S
completion-queue drops** during steady FLAC playback. There were no write
errors or arena allocation failures. Arena live storage stayed at **53,024
bytes in 12 blocks**, with **45,872 bytes free**. That trial alone did not
establish an allocator regression; the contemporaneous no-arena comparison
had not included FLAC.

The failing interval followed an RSSI change from approximately -61 to
-77/-80 dBm. In the matching host delivery window, one socket write took
**416 ms**, and cumulative delivery lateness increased to about 835 ms.
Host write completion is not a board receive timestamp: TCP backpressure,
network loss and device scheduling can all affect it. The old recording has
no per-overrun task checkpoints, so its exact cause cannot be proved after
the fact.

## Meaning of the counter

The pinned ESP-IDF `i2s_common.c` TX callback removes an old completion
notification when its queue is full, invokes `on_send_q_ovf`, then enqueues
the newly completed DMA buffer. This is a queue of **finished buffer
addresses**, not queued audio packets.
The driver allocates `dma_desc_num - 1` notification entries: **3 entries**
for this firmware's **4 DMA descriptors**.

In this firmware, the output task waits for PCM when none is available.
`native_audio_output_idle()` does not stop DMA; descriptors clear to PCM
zero. Consequently, loss of input data can exhaust PCM, stop calls to
`i2s_channel_write`, and fill the completion queue while DMA keeps running.
The counter also increases during normal idle/EOF, which must be excluded
from playback measurements. Four 512-frame descriptors at 48 kHz cover
about **42.7 ms**; a descriptor completes every **10.67 ms**. Drop count is
not a direct count of audible clicks or missing PCM samples.

## Memory interaction found in the code

`tls_input_reserve_expand_flac()` attempts four additional encoded packet
slots after the first decoded FLAC frame, but only while preserving
`FLAC_INPUT_HEAP_HEADROOM = 32 * 1024` bytes in the **system heap**.

The private arena cannot fund these allocations, even when half empty:
network packets are intentionally outside it. The arena therefore has an
indirect effect on FLAC's tolerance of delivery pauses. In the diagnostic
arena runs, the queue limit was 8 slots but only **4 were resident**, each
2,060 bytes including its header (2,048 encoded payload bytes). During
steady playback the system heap was below the expansion threshold.

At this fixture's approximately 1.29 Mbit/s average encoded rate, four
payload slots represent only about **51 ms** of compressed data, versus
102 ms for eight slots. These are capacity estimates, not measured total
pipeline latency: TCP, the partial FLAC frame, PCM and DMA also buffer data.
The one-second startup prefill is a waiting policy, not a guarantee that a
full second of high-bitrate FLAC fits in memory.

## Diagnostic implementation

All new firmware telemetry is behind
`CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC`, still disabled by default:

- The existing 16-event ISR history records output/decoder/HTTP call phases
  and the age of the last PCM, encoded packet and successful HTTP read.
- `input_queue` reports resident/occupied slots, minimum, limit and packet
  capacity. Its snapshot is separate from the ISR snapshot.
- `arena_timing` reports `[lifetime call count, maximum microseconds]` for
  private malloc, free, realloc and heap statistics. Counts use uint32 wrap.
  The measurements include allocator/copy/heap-walk work inside the lock,
  excluding lock entry/exit and accounting afterward. They are observed
  maxima, not proven worst-case bounds; initialization, calloc zeroing and
  system-heap allocations are not measured by them.

The runner supports distinct repeated trials and exact-byte delivery pauses.
Its explicit `--collect-after-fault` mode preserves fault counters and allows
diagnostic collection to continue; **acceptance gates still fail**. The
review script isolates DMA deltas while reporting the actual fault counters,
never turning that diagnostic calculation into a qualification pass.

## Completed quiet-image control

The same synthetic `flac-level8` fixture (1,771,852 bytes, 11 seconds,
48 kHz stereo) was played five times on each image. The reported window
starts at the first observation at least three seconds after Play and ends
around eight seconds; it does not cover the whole file. EOF was checked
separately. Radio conditions were not held constant.

| Image | New completion-queue drops by trial | New write errors |
|---|---|---|
| Quiet no-arena control | 0, 0, 0, 0, **8** | 0 |
| Quiet 100 KiB arena, completed retry | 0, 0, 0, 0, 0 | 0 |

This reproduces the symptom without the arena; it does **not** show that the
arena is more reliable. The control RSSI varied from -71 to -58 dBm and the
arena retry from -69 to -53 dBm, with only five trials per image.

Two earlier arena starts failed the lifetime allocation-failure gate before
the first fixture. The first controller did not retain the offending health
row (the terminal traceback identifies the failure); the second retained a
count of 3. Both aborted trials and successful restorations are included.
The successful third startup does not supersede them. The no-arena control
also retains two failed short-window heap-trend gates, despite zero system
allocation failures; this investigation does not relabel them as passes.

The three unpaused diagnostic arena runs had **zero new DMA drops**, zero
steady malloc/free/realloc calls, and 4 resident input slots. Observed
allocator maxima included 191 microseconds for realloc and 26 microseconds
for statistics. All three retained the same three system allocation
failures from startup, so their acceptance result remains FAIL. Three more
diagnostic arena runs with a requested 450 ms host pause also had zero DMA
drops: the remaining buffering absorbed this particular intervention.
Those runs retained one startup allocation failure. This is why host pauses
must not be equated directly with device receive gaps.

## Controlled one-second delivery pause

The fixture server paused before encoded byte 900,000, without shifting its
subsequent pacing deadlines. Both builds used the same fixture, pacing,
pause schedule and observation logic. Each trial reached EOF; no write
errors occurred.

| Diagnostic image | Resident input slots | New DMA drops by trial | RSSI across steady windows |
|---|---:|---|---|
| No arena | 8 | 47, 48, 47 | -69 to -59 dBm |
| 100 KiB arena | 4 | 49, 23, 130 | -84 to -60 dBm |

**All 344 drops** occurred while the output wait flag was set. In 138/142
control drops and 187/202 arena drops, the decoder input wait and HTTP read
flags were also set. The remaining events occurred while waiting for PCM
after the other phases had advanced. The flags are call checkpoints, not
proof of a FreeRTOS blocked state. However, retained events show the output
checkpoint continuing to advance (ages at most 10.051 ms in control and
5.885 ms with the arena), while PCM/encoded/HTTP checkpoints aged by
hundreds of milliseconds. This supports **input/PCM starvation**, not the
output task being denied CPU for the entire gap.

The arena performed **zero malloc/free/realloc calls throughout every
steady observation window**, including all three faulty paused windows.
The maximum measured statistics walk was **27 microseconds**. Observed
realloc work during setup stayed below 0.2 ms in these runs. The diagnostic
data does not support private-allocator lock latency as the direct cause of
these long gaps. It does not qualify worst-case latency for other codecs,
allocation patterns or cache conditions.

The paused arena boot already had 9 system allocation failures before FLAC;
the count did not increase during these fixtures. The no-arena control had
zero. All acceptance FAIL results are retained. The 16-event history also
overwrote events between samples: the per-phase histogram covers every
counted event, but detailed ages exist for only 88/142 control events and
93/202 arena events. These missing details are reported explicitly.

Signal and delivery varied sharply in the last two arena trials. Therefore
the drop totals cannot quantify a reliable arena-versus-control failure
rate or the benefit of four more input slots. What is established is:

1. Input starvation reproduces the completion-queue symptom on both builds.
2. In the arena diagnostic, starvation happens without ongoing arena
   allocation/reallocation; the output task still reaches its checkpoints.
3. The arena reduces actual FLAC input capacity from eight slots to four by
   leaving insufficient system headroom for the existing expansion policy.

For the original October 12 failure, network/input starvation is the best
supported explanation, with the smaller input reserve a plausible
aggravating factor. The original recording cannot establish that causal
chain as conclusively as these instrumented reproductions.

## Replay and validation

The [raw evidence](../tests/results/esp32c3-arena-flac-dma-20261013/) includes
failed starts, unchanged acceptance gates, status/health/arena/input/timing
samples, host delivery windows and pause timestamps, exact controller
sources, configuration/link checks and restoration records. Controllers
retain only whitelisted technical status; Wi-Fi credentials, saved station
identity and settings snapshots are not written to the archive.

`decoder_arena_experiment.py` accepts `--repeat 3` and
`--delivery-pause 900000:1.0` for these trials. Deliberately paused playback
is a diagnostic stress test and must not be reported as qualification PASS.
Replay each completed phase with:

```powershell
python -B -X utf8 tools/esp32c3_tests/decoder_arena_flac_review.py `
  tests/results/esp32c3-arena-flac-dma-20261013/probe-pause1000-paired `
  --label candidate --output .build/arena-flac-review.json
```

Use `--label baseline` for the control. Replay rejects mismatched sample
counts or duplicate trial names; it explicitly reports fault-counter ranges
even when calculating DMA deltas from a failed run.

Validation: 15 Python unit tests passed, covering malformed telemetry,
diagnostic fault preservation/reboot rejection, distinct trials, EOF
exclusion and pipeline history retention. Both regular and diagnostic
allocator host tests passed ASan/UBSan, including realloc preservation,
domain ownership, exhaustion, coalescing and concurrent reuse. The
diagnostic host clock is synthetic and tests accounting only. SDK objects
retain the previously documented host-only alignment-sanitizer exception.
Both target diagnostic builds succeeded; their enabled configuration
difference is exactly the arena switch and its 102,400-byte capacity.

Saved diagnostic images:
[arena](../firmware/development/esp32c3-idf-6.1-r9a97-arena-dma-probe/app.bin)
and [control](../firmware/development/esp32c3-idf-6.1-r9a97-flac-dma-control/app.bin).
Both are marked hardware-tested and **not production-qualified**.
Every one of the six test-controller runs restored the original
`idf61-production-prefill1000` application (ELF SHA-256
`73da8e2146c5b3691bcfc7a8fb46b34109e74099eac221df2b66e05a62b95245`),
verified unchanged Wi-Fi/playlist/settings, and resumed the original station.

## Limits and next action

Do not lower the 32 KiB safety threshold merely to make a test pass. The
100 KiB arena already produced intermittent system allocation failures at
startup, before any fixture. Successful playback on another boot does not
clear that failure. Keep the arena experimental and disabled by default.

A follow-up design should budget decoder storage and encoded-input capacity
together, allowing safe reuse of genuinely unowned storage between codecs,
while retaining TLS/Wi-Fi/WebUI headroom and checking all pointer lifetimes.
Increasing the DMA notification queue alone would mask this symptom without
supplying missing audio. No allocator, codec arithmetic, scheduler priority,
DMA queue size or production default was changed in this investigation.
