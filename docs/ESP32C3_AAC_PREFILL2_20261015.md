# Two-second AAC startup-prefill experiment

## Result: no measured continuity improvement

The existing initial-input wait was increased from one to two seconds with
the AAC extra-slot option disabled. The matched controlled TLS pause test still
fails its output check: **50 new DMA completion-queue drops**, versus 48 in the
one-second baseline. Both pass 10/11 checks, with zero allocation, decoder,
watchdog or output-write errors. The two-event difference from one observation
does not establish a systematic regression, but provides no reason to promote
the longer wait. Production settings remain at one second.

| Measurement | One second | Two seconds |
| --- | ---: | ---: |
| Actual short / medium / long host pauses, s | 0.5121 / 1.0032 / 1.5103 | 0.5029 / 1.0080 / 1.5154 |
| New completion drops near those pauses | 0 / 0 / 48 | 0 / 2 / 48 |
| Actual resident input slots / limit | 4 / 4 | 4 / 4 |
| First sampled matching decoded format after observation starts | 2.325 s | 3.392 s |
| Minimum sampled free heap / largest block | 59,152 / 32,768 B | 59,256 / 32,768 B |
| Settled free-heap median before / after Stop | 138,928 / 138,932 B | 138,920 / 138,968 B |
| Settled largest block before / after Stop | 114,688 / 114,688 B | 110,592 / 110,592 B |

The fixture, byte offsets, 1.0 pacing, 4-KiB host send buffer and TLS 1.2
ECDHE-RSA-AES256-GCM-SHA384 cipher match the
[one-second control](ESP32C3_AAC_TLS_PAUSES_20261015.md). Both use the owned
AAC-LC 44.1-kHz stereo source, SHA-256
`65feca3e7d6f0a87fb411488aa146a736da097b685772b00438d300268e0f9e7`.
Start timing is sampled matching status, not the exact first audible sample.

The new run retains 106 health observations on one boot and 68 steady-state
format samples. Last status is at 89.369 seconds of the requested 90 seconds.
The retained all-wait ISR events have output-checkpoint ages 0.021–4.684 ms,
while PCM/encoded/network checkpoints become stale. These data support input
starvation in this imposed schedule, not a missing output-task priority boost.
They do not establish the cause of previous public-source failures or measure
the analog signal.

## Build and host verification

Image `idf61-aacpf2-20261015`, source `db34871a`, app SHA-256:
`76975ab84af607702b9325e465053c3d1af34322cbd3e279825b3ca374cf375a`.
The normalized configuration comparison against the local-CA baseline proves
exactly two differences: `INPUT_PREFILL_MS` and `INPUT_PREFILL_MIN_MS`, both
1000 → 2000. Extra AAC slots are zero; TLS reservation, full record size,
public trust roots, DSP, QIO 80 MHz, priorities and exact nominal 48-kHz output
remain the same. Linked DRAM, IRAM and RTC section sizes do not increase.

Kconfig previously capped the experimental interval at 1000 ms. Its allowed
maximum is now 2000; defaults did not change. The initial build recipe also
reapplied the one-second tested profile and was discarded before deployment.
The corrected recipe starts from that profile's saved complete configuration
without reapplying it. Final configuration and image audits pass.

All 28 ASan/UBSan prefill variants pass (ring/adaptive queues, 500/1000/2000-ms
maximums and multiple minimums). They exercise actual prefill code with
deterministic time/queue stubs: full/sparse queues, cancellation, generation
wrap and coarse ticks. This proves bounded host behavior, not physical
Stop/replacement latency or full codec qualification.

Original production firmware, Wi-Fi, playlist and settings are verified
restored, with playback stopped. The physical archive retains the pre-test
firmware manifest; the artifact's current manifest records the failed result.

[Build evidence](../tests/results/esp32c3-aac-prefill2-20261015/build/),
[host tests](../tests/results/esp32c3-aac-prefill2-20261015/host/), and
[physical observations/restoration](../tests/results/esp32c3-aac-prefill2-20261015/physical/)
are preserved.

## Next decision

Longer waiting alone does not create persistent storage once the existing
queue is full. Do not increase the production delay on this evidence. Revisit
[guarded input growth](ESP32C3_AAC_INPUT_GROWTH_20261015.md) with explicit
ownership of memory needed by late SBR/PS. Measure whether retaining that owner
and adding bounded input slots fits the actual worst-case decoder/TLS workload;
do not simply bypass its safety guard. Check real resident capacity before
interpreting an output comparison. The public AAC output failure, intermittent
FLAC/WebUI timeout and final all-format production qualification remain open.
