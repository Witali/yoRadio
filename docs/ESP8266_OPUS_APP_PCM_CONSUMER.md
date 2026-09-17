# Experimental PCM consumer on the existing app task

2026-09-17. `-Diagnostic -EnableOpus -OpusPcmQueue -OpusPcmAppTask`.
Off by default; not yet qualified for live radio.

The existing3072-byte app task services at most one decoded mono20ms frame
per loop, then returns to BOOT/control/background work. The same two leased
960-sample PCM slots are used; no copy, new task or extra consumer stack.
DMA conversion stays in task context, not in the ISR. Backpressure uses the
existing task notifications and always rechecks queue/buffer predicates.

On begin the app priority becomes6 (same as the separate consumer); on stop
it returns to its original priority. Stop waits until all producer/consumer
loans have ended before the decoder can reset/free memory. Startup deinit
must not delete the app task. Decoder arithmetic and PCM block order are
unchanged. The main decoder stack stays5120 bytes, WebUI stack5120 bytes.

Frequent PCM/DMA wakeups do not cause HTTP work on every frame. Actual native
state changes have a sticky service flag that survives a DMA wait consuming
the task notification; BOOT events remain in their existing queue. Services
otherwise retain250ms polling, LED its independent cadence. Flash/settings
work may still delay this consumer; this is a risk to measure, not a promise
that sharing the app task is always suitable.

Against the dedicated consumer this removes its configured1536/2048-byte
stack plus TCB, adding only a saved priority and state-notification flag.
Against synchronous DMA512, PCM2x960 adds1920 bytes and DMA2x128 saves3072
bytes: nominal buffer saving1152 bytes before control structures. Actual ELF,
heap, stack margins and physical continuity must be measured on the board.
The4096-byte Opus reserve and6144-byte scratch are not reduced.

Local tests cover actual queue ownership under ASan/UBSan, exact sample order,
pre-skip offsets, full-queue blocking,25 in-flight stops, output failure/reuse,
priority restoration and prohibition on deleting the shared app task. The
real app loop is tested with frequent PCM wakeups, immediate control events,
tick wrap and delayed background work, with LED OFF/10/20Hz. Native-state
tests distinguish real status changes from PCM-only wakes.

## Background-service attribution (diagnostic app mode only)

The four additional uint32 counters cost16 static bytes, no heap or task.
They measure the interval after each PCM poll and before sleeping: controls,
background network/time/WebUI/storage service and wait-deadline calculation.
`GET /api/native/audio?pcm=1` returns calls, total/max wall microseconds and
DMA underruns observed inside that interval. The normal health response
does not grow. Startup before the first PCM and stopped neutral output are
not counted; all active intervals, including preemption, are retained.
Counters reset on queue begin and wrap modulo2^32. This is not CPU time or
proof that the service itself (rather than preemption) consumed the interval.
No changes to decoder arithmetic, output pacing, priority or memory guards.

## DMA192 follow-up hypothesis

DMA128 steady Kultur24 samples still show short misses without input waits.
Full960-frame PCM output leaves a64-word tail with128-word DMA, while192
divides960 exactly. Diagnostic192 gives4ms per full block, adds512 DRAM bytes
versus128 and needs512 fewer bytes than the rejected256 variant. No padding,
new copy, PCM samples or PDM decisions are introduced; pre-skip and other
valid frame lengths still use exact partial descriptors. Default remains512.
Physical qualification is required; divisibility alone does not prove a fix.

The appdiag board also returned an implausible service maximum4294966397us,
consistent with a small backward step of the SDK microsecond clock. Such
wall timing is invalid, not a multi-hour service delay. Keep the raw evidence;
DMA miss and tick-based continuity counters are separate. No CPU claim.
