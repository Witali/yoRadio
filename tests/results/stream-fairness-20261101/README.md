# Stream-owner fairness: HOST and compiler checkpoint

The HTTP stream owner could keep receiving positive reads and publishing into a
fast queue without blocking. This left no guaranteed opportunity for lower
priority idle work. Historical family1 native05 genuinely reported IDLE0
starvation with CPU0 in radio_stream; that isolated diagnostic is NONPASS.
It is not a physical timing, OOM, codec or stack-failure result.

Committed change `7ea48df71bb9605e5a70f935ff649a01d9b23c2f` adds the same pure
20,000-microsecond elapsed budget to CYD and C3 HTTP body loops. When due, the
owner blocks for one RTOS tick, rebases after that wait and continues to the
loop condition before another read. Positive audio, ICY metadata and EAGAIN all
share the budget. Payload, retry, availability, framing and EOF behavior remain;
task cores/priorities/stacks, watchdog policy and hardware settings do not change.

| Completed evidence | Result and scope |
| --- | --- |
| C3 plain02, retained-RX/adaptive01, FLAC-growth/shared-power01 | 42/42/47 ASan/UBSan HOST cases. Five new actual-loop schedules compare positive audio, sub-slice no-delay behavior, split ICY+retry audio/title and Stop during positive/EAGAIN fairness waits. |
| CYD stream02 | 55 stream cases and80 settings requests using actual production task/handler bodies with explicit SDK/RTOS/output seams. |
| Shared power02 | 10 C3 controls,9 CYD controls and9 CYD receive groups; unchanged generation/lifetime/power assertions. |
| CYD syntax01 | One actual pinned Xtensa syntax-only child exited0 with78 source bindings and zero diagnostics. No target was executed. |

The C3 clock getter remains side-effect-free. Only modeled transport work and
actual modeled waits advance its clock. One original two-second retry assertion
now explicitly accounts for exactly one added tick atop its unchanged two
one-second reads. These model times are not MCU throughput or idle guarantees.
The old-generation terminal marker after Stop remains unchanged; the tests
check its generation and prevent another read/audio publication after the wait.

All three first new-harness failures remain exact and separate: C3 plain01
incorrectly expected no terminal marker after Stop; CYD stream01 lacked the
default-off TLS helper include; power01 lacked an output-metrics header.
Their corrected successors preserve the original production assertions.

The historical native05 audit binds13 complete references,21 complete application
cases and17,579 complete matching after-write records. One final record interleaved
with the watchdog is explicitly unclaimed. Its old33-source release and snapshots
authenticate that history; current-source equality is not retroactively required.
Full UART containing PCM, PCM files, executables and flagged original files remain
local whole. The manifest records their exact identities and omission reasons.
No scanner result is overridden or used to relabel unsafe bytes as acceptable.

`captures.zip` deduplicates byte-identical original reports/logs/snapshots; it
does not rewrite them. Verify only the saved data with:

```text
python -B tests/results/stream-fairness-20261101/verify.py --require-current
```

This verifier never compiles, executes archived code, decodes PCM or reads omitted
payloads. C3 own-SDK compilation and complete native fairness qualification remain
open. Full-radio Wi-Fi/TFT/DMA memory, physical timing, audio quality and prolonged
board playback also remain open. The ordinary FLAC successor is unchanged and
held until the final production source is qualified.
