# ESP32-C3 staged-output queue-wait diagnosis — 2026-10-09

## Question and implementation

The [controlled TLS follow-up](ESP32C3_TLS_FINAL_GATES_20261009.md) found DMA
completion-queue events with 16 KiB records, despite passing playback and
memory gates. This experiment distinguishes empty encoded input, full PCM
queues and empty PCM at the output. It does not change buffer capacities,
decoder arithmetic, priorities, timeouts or PCM samples.

Commit `4d6307e` extends the default-off
`CONFIG_YORADIO_PIPELINE_PROFILE` to staged output. The direct backend retains
its existing measured DMA-wait field. Staged output uses the distinct
`PERF FLOW_STAGED_OUT` marker: it reports empty-PCM wait and total submission
time, and omits the unavailable separate DMA-wait measurement. A zero value
must not be substituted for an unmeasured quantity.

The C host harness compiles the actual queue wrappers and extracted reporting
helpers for enabled/disabled probes and staged/direct output. All four variants
pass ASan/UBSan checks, including counter wrap, report reset, inactive periods
and an ISR event during logging. Five parser tests and four historical-evidence
tests pass; older direct-output summaries remain identical.

## Matched images

The control is the saved `idf61-pcm-tail` image. The new saved
[diagnostic image](../firmware/development/esp32c3-idf-6.1-r9a97-staged-flow/)
is `idf61-staged-flow`, 1,622,112 bytes, SHA-256
`5f01f51c323d48e3ad59f198f0bb6b5e0615baedd84ba6359ffe15acc83cbea0`;
its ELF identity is
`8001f8731f9d12b0bb1f916a37c96792ef0b0c91d27ca846cec1eb8e457c6acd`.
Only `CONFIG_YORADIO_PIPELINE_PROFILE=y` changes in the effective configuration.

Both use the pinned ESP-IDF revision `9a97f6c54ec638111ce55cd36581b3c192f15207`,
full compact AAC/SBR/PS, the RX-only TLS reserve and adaptive queue, maximum
500 ms prefill, QIO 80 MHz and nominal fractional 48 kHz output. Fresh startup
registers and four mapped application CRC checks are retained for each image.
Linked-code audits verify full AAC and the guarded HTTP reader. The unrelated
CLZ CMake block is inactive.

IRAM text remains 47,690 bytes, DRAM data 12,856 bytes and BSS 45,664 bytes.
Diagnostic counters are task-local and use stack space within existing task
stacks; unchanged BSS does not mean the instrumentation has no cost. This is a
laboratory image with an extra test CA, not a production release.

## Short physical comparison

Each image plays the same full HE-AACv2 44.1 kHz stereo fixture over TLS 1.2
AES-GCM, first with 1 KiB records, then 16 KiB records. Each case lasts 75 s;
delivery is explicitly 1.0x. CPU, heap and cumulative DMA comparisons exclude
the first 10 s and require complete telemetry. These sequential observations
are not enough to isolate compiler-layout or RF effects on CPU usage.

| Image / records | Mean CPU busy | Minimum CPU-log free heap | Minimum largest block | Selected DMA queue events | Driver errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| Control / 1 KiB | 61.830% | 26,256 B | 15,360 B | 0 | 0 |
| Control / 16 KiB | 60.937% | 26,264 B | 15,360 B | 6 | 0 |
| Profile / 1 KiB | 59.432% | 26,224 B | 18,432 B | 0 | 0 |
| Profile / 16 KiB | 58.591% | 17,208 B | 7,680 B | 4 | 0 |

All original short-case playback, runtime and settled-memory gates pass.
The queue-event problem reproduces with profiling off and on. Lower measured
CPU in the instrumented image is not claimed as a speed improvement.

| Complete selected profile windows | 1 KiB records | 16 KiB records |
| --- | ---: | ---: |
| Encoded-input wait, total | 0 ms | 454.618 ms |
| Encoded-input wait calls / timeouts | 0 / 0 | 27 / 12 |
| Encoded-input wait, longest call | 0 ms | 24.827 ms |
| Decoder waiting for PCM space | 55.340% | 54.890% |
| Output waiting for PCM, total | 371.554 ms | 807.996 ms |
| Output waiting for PCM, share of wall time | 0.618% | 1.344% |
| Empty-PCM timeouts | 7 | 92 |
| PCM submission, share of wall time | 99.204% | 98.474% |

Percentages refer to each task's own observed windows. They overlap and must
not be summed as CPU utilization. Submission includes copying, DMA waits and
preemption; the driver does not expose those components separately.

Two selected output windows each contain two queue events. In the overlapping
decoder windows, encoded-input waiting is 102.052 ms (four timeouts) and
94.490 ms (three timeouts). The corresponding output windows have 23 and 18
empty-PCM timeouts. This supports transient input starvation as a contributor.
Five-second aggregates cannot establish the exact duration of an audible gap
or exclude scheduling effects inside each interval.

## Ten-minute observation and limits

The instrumented image completed the full 600 s alternating 1/16 KiB record
case at 1.0x delivery. All 17 original entries across the three phases pass;
there are no recorded allocation failures, crashes, watchdog resets, driver
write errors or client transport exceptions. The earlier Windows `10048`
failure did not recur in this run. Original playback gates do not reject DMA
completion-queue events, so their PASS does not establish gap-free output.

After the first 10 s, mean CPU busy is 58.656%, the minimum CPU-log free heap
is 26,260 B and the minimum largest block is 18,432 B. Complete selected flow
windows show 1,619.286 ms waiting for encoded input (149 calls, 39 timeouts),
55.507% waiting for PCM space, and 4,693.634 ms waiting for output PCM
(0.801% of wall time, 285 timeouts). The largest individual empty-PCM call is
11.454 ms. Repeated timed waits can form a longer uninterrupted starvation
period; that individual maximum is not an upper bound on an audible gap.

| Observation | DMA queue events after warm-up | Events across the whole observed counter interval |
| --- | ---: | ---: |
| Control / 1 KiB, 75 s | 0 | 0 |
| Control / 16 KiB, 75 s | 6 | 6 |
| Profile / 1 KiB, 75 s | 0 | 0 |
| Profile / 16 KiB, 75 s | 4 | 6 |
| Profile / alternating records, 600 s | 5 | 6 |

The whole observed interval is bounded by captured counter reports; it is
not a sample-accurate measurement of startup or sound. Instrumented task-stack
minimum free space across these cases is 1,104 B for output, 2,564 B for
decoding and 2,564 B for streaming. These observations do not justify reducing
task stacks.

The controller restored `idf61-qio80-8c1f2d2d`, verified unchanged Wi-Fi,
playlist and settings, and recorded three successful AAC 44.1 kHz stereo
playback observations. It used application-only OTA.

## Candidate follow-up

The existing maximum prefill exits early when the queue fills, after about
9 ms for bursty full records. Small records instead use the 500 ms deadline.
Commit `f2d94570` adds an experimental, default-zero minimum prefill. A 250 ms
minimum retains the same queue and the same 500 ms deadline; Stop and new
generations cancel promptly. The [completed separate comparison](ESP32C3_MIN_PREFILL_20261009.md)
records zero observed DMA queue events for that candidate, including its
600 s alternating-record case. It is not part of the measurements above,
and broader candidate qualification remains open.

No acoustic capture or listening comparison is available. Fractional clocking
and minimum prefill remain experimental. This diagnosis does not qualify all
public stations or the final quiet production configuration.

## Reproduce the evidence analysis

The [frozen evidence](../tests/results/esp32c3-staged-flow-20261009/) contains
the original verdicts, raw filtered observations, per-request transport
timings, build and host checks, and 88 source snapshots. The measured source
is commit `4d6307e` with the build overlay hashes recorded in the manifest;
the later minimum-prefill implementation is not used to reinterpret this
run. Public test certificates are included; private keys and saved settings
are excluded.

From the repository root, run:

```powershell
python tests/results/esp32c3-staged-flow-20261009/replay.py --output .build/replay-staged-flow
```

Use a new output directory. Replay verifies byte hashes and reproduces all
metrics and original verdicts. The evidence verifier's PASS means identity,
restoration and verdict preservation; it does not override the queue events
or qualify analog sound quality.
