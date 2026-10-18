# CYD SMP health core preparation

[The host test](../../run-cyd-health.py) compiles the actual fault, optional
CPU sampler and bounded JSON formatter implementations under ASan/UBSan.
[The report](report.json) records source hashes for quiet, diagnostic32 and
diagnostic64 variants. Pipeline/HTTP wiring and SDK/hardware qualification
are not yet included in this preparation stage.

- 60,000 allocation, decoder, stream and output events per category per
  variant from two pthread writers; snapshots retain coherent tuples and
  all increments. Quiet mode creates no sampler and makes no IPC call.
- Two-core CPU denominator and per-core idle accounting, task percentages
  expressed as one core's capacity, 32/64-bit global/task/idle counter wrap,
  first/zero samples, task handle reuse with a new task number, replacement
  during sampling, absent SDK snapshots and IPC failure.
- Deleted-task name pointers are deliberately invalid in the SDK seam;
  the implementation never dereferences them. It uses registered handles
  and SDK-copied numerical fields, including stack high-water bytes.
- Callback registration/sampler creation failure, and retries after those
  failed starts, preserve usable quiet counters.
- Every JSON capacity is checked with canaries; uint32/uint64/int32 maxima
  fit 2,304 bytes and parse with Python JSON. Unavailable CPU and stack
  measurements are `null`, including the quiet profile.

Mutexes and conditions are real host primitives; SDK tasks, IPC, scheduling
and ISR entry are seams. Passing tests do not qualify physical ISR latency,
stack headroom, CPU overhead or playback timing. The proposed sampler uses
the public IPC API in diagnostic mode to account for the other core's cached
runtime before a snapshot; its overhead needs board measurements.
