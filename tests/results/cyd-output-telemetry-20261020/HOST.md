# Coverage and interpretation

The new backend suite compiles byte-exact frozen `native_audio_output.c` and the
complete real `native_output_metrics.c` as separate translation units. SDK driver,
GPIO, delay, clock and pthread critical-section seams share consistent ESP-IDF
error values. Public output APIs and snapshots drive the suite; it never seeds
private counters, owner phases or ACK state.

An independent ledger records actual synchronous driver calls. Tests cover prime
writes, request/reported byte units, full chunks/tails, PDM padded flush, DAC and
legacy idle, failures/timeouts/short writes/over-reports, and paused requests
excluded before driver invocation. PDM registration failure cleans up before
preload/enable and leaves queue observations unavailable. Successful registration
exposes the actual ISR hook; 10000 callback invocations overlap 100 real public
PCM writes and coherent snapshots. Existing GPIO26, clock, channel/slot, DMA and
timeout settings are asserted at the driver boundary. Preloads are excluded from
synchronous driver-write counts.

The eight integration controls remove each backend hook, change legacy request
units, ignore registration failure, prematurely advertise queue availability,
remove the registered ISR increment, or omit the DAC idle hook. Each must exit
with the expected named semantic failure rather than a sanitizer/build failure.
The counter suite separately exercises invalid clocks, saturation, coherent
concurrency and quiet mode with seven exact controls. Its boundary-only source
initializers are explicitly reported and are not runtime writes to private state.

The old suites retain their original scope through an explicitly empty metrics
fixture dependency, captured by each report: pause 11/17/10 cases plus two
ownership controls; gain 5801300 arithmetic and 375 producer cases per backend;
normalizer 239/240/239 packets; packed PCM 1359/1358/1358 stream cases; maintenance
with actual network-power policy 83 cases and nine controls. PCM references and
production algorithms were unchanged. Stale test-only DAC enabled state/pause
declarations and the extractor's ability to select macro call sites were repaired.

Health qualification runs quiet, diagnostic32 and diagnostic64 profiles. Maximum
counter widths produce 2000-byte JSON within the 2304-byte buffer; every tested
capacity preserves canaries. Unavailable queue/timing values remain null while
measured zero stays numeric. These serializer values are scripted snapshot
inputs, not real driver measurements. The stream gate checks actual HTTP/ICY,
probe/settings/status handlers with an explicit output-driver snapshot seam;
it does not execute NVS transactions or backend I/O. Historical stream01 has no
saved failure output; stream02 preserves its obsolete host `xQueueReceive`
wait-contract assertion. Successful stream03 is the authoritative qualification.

The actual SDK 6.0.2 Xtensa helper objects have a 50-byte queue-drop function in
`.iram1.2`, 64-byte metrics state and an 8-byte lock in DRAM. The inlined increment
calls no allocator, libatomic or wall-clock API. The normal valid-lock path calls
SDK IRAM enter/exit primitives; compare-and-set is IRAM and interrupt restore is
ROM in the bound existing baseline ELF. SDK spinlock contention can read the raw
CPU cycle counter. This object review predates backend wiring and preserves its
historical context hashes. Current helper dependency hashes still match; final
metrics03 and the independent integration review supersede its earlier host
fixture hashes. The raw object report's literal-relocation field is empty; the
final review verifies actual `R_XTENSA_ASM_EXPAND` callee records in both objects.

Clang source/header/config closure and raw diagnostics/YAML/dependency logs are
included. The warning comparison preserves translation-unit/file identity,
severity, check, full message and multiplicities while normalizing build paths
and ignoring line/column offsets. N5 had 52 units and 86 warnings; this run has
53 units and the identical 86-warning multiset. The new metrics unit has zero
diagnostics. `lint/diagnostic-comparison.json` records an empty added/removed diff.

ASan/UBSan use fail-fast settings. Pthread seams do not reproduce ESP32 scheduler
or ISR timing. The independent review checks pinned SDK contracts and records
open/seamed paths. Final linked callback/helper placement, physical interrupts,
SMP latency, DMA, audio quality, resource margins and overhead remain separate
qualification work. No new application build, flash, serial, physical I/O or
network download was performed for this archive.
