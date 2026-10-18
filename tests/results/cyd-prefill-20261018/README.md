# CYD bounded first-input prefill

The CYD default remains zero (disabled). Configured waits are limited to
0–2,000 ms and end when storage is occupied, a logical deadline is reached,
or the generation is cancelled/failed. Scheduling latency is not qualified.

[The standalone test](prefill/report.json) compiles the actual private
production helper under ASan/UBSan with scripted queue/time/task seams. It
covers disabled/full/empty input, filling during a wait, timeout, cancellation,
output failure, a coarse 20 ms tick, 64-bit time past UINT32_MAX and occupied
WRITING/READING leases with no ready audio.

[Lifecycle integration](lifecycle/report.json) executes actual decoder/output
tasks and state functions in six ring/leased-queue and codec combinations.
The three leased-queue branches enable a 250 ms prefill in the host build.
Assertions check that Stop returns the held input without decoder allocation,
startup control replay bypasses the wait, and AAC-to-MP3 drain in one generation
does not wait a second time. Codec and queue APIs are scripted here; the actual
shared queue has independent [concurrent ownership coverage](../cyd-c3-frames-20261018/README.md).

This is software coverage, not a measured CYD network-jitter or audio-quality
improvement. SDK build/firmware evidence is recorded separately when complete.
