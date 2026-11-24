# CYD WebSocket polling on shared SDK tasks

The scheduler removes the dedicated 2,048-byte WebSocket polling stack.
An ESP Timer callback posts a zero-wait, payload-free event; the existing
event-loop task enqueues HTTPD work. Both stages coalesce into one pending
poll. The [implementation and ownership contract](../../../docs/CYD_WS_SCHEDULER.md)
retain the 100 ms period, full messages, two clients and the audio task
cores/priorities/stacks.

The current source completes full TLS/HE-AAC, exact PCM, live WebSocket
commands and WebUI after EOF on each output. Its first continuous-DAC run
also has a genuine output timeout, retained as NONPASS. A subsequent run of
the exact same linked image passes. **Continuous-DAC repeatability remains
open**; this archive does not explain or erase that timeout.

## Current-source observations

All retain normal TCP RX 11,520 / mailbox 10 / TX 5,760, full TLS buffers
16,384/4,096, no separate static-RX loan, five-second task watchdog and
300 ms interrupt watchdog. The opt-in RTC workspace is enabled in these
diagnostic runs; its 6,560-byte object capacity is unchanged.

| Output / run | Original outcome | PCM at ordered EOF | Allocation failures at EOF | Minimum free heap at EOF |
| --- | --- | ---: | ---: | ---: |
| PDM | PASS | 614,400 frames | 0 | 2,332 B |
| Legacy DAC | PASS | 614,400 frames | 0 | 1,820 B |
| Continuous DAC, first | NONPASS: audio output failed | No complete flush | No EOF sample | No EOF sample |
| Continuous DAC, exact-image control | PASS | 614,400 frames | 0 | 5,704 B |

Each complete run receives all 102,420 original encoded bytes, verifies
full TLS 1.2 AES-GCM records and emits the unchanged PCM SHA-256
`44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`.
The exact 13,588-byte static asset is read during playback and after EOF.
Both clients receive newer idle/playing/EOF status, three application pongs
and a normal close code 1000. Decoder archives and PCM contracts are unchanged.

The failed continuous run makes progress before reporting `ESP_ERR_TIMEOUT`
from the DAC write path. Its last reachable health has zero allocation
failures. It does not complete the EOF asset/client checks. No firmware,
configuration, QEMU executable or requirement changes separate that failed
run from its passing control. The
[earlier continuous-DAC qualification](../cyd-dac-production-20261113/README.md)
also preserves timeouts, but does not establish this timeout's cause.

## Memory comparison and limits

All seven new runs report 17 tasks initially, versus 18 in their respective
[previous two-client controls](../cyd-ws-rtc-memory-20261124/README.md).
Early health snapshots show 1,872–2,156 more free bytes, depending on the
run. These are observed snapshots with asynchronous network activity, not
an exact allocator-accounting identity. The linked BSS increases by 16 bytes;
the timer and permanent handler also consume memory. The removed stack
constant alone must not be reported as the total recovered heap.

The effective configuration is identical to each matching previous
profile. The sole changed project C translation unit is
`websocket_service.c`; all other project-TU hashes match. The records pin
the actual linked ELF/map/config/commands without publishing those build
products or claiming a full compiler dependency closure. Diagnostic RTC
usage remains 6,664 bytes with 1,504 bytes below the separate reservation.

Heap minima remain small. A finite zero-allocation-failure result does not
establish margin for arbitrary traffic or physical Wi-Fi operation. The
RTC option remains disabled by default. Normal production exports with
the new scheduler/RTC combination and physical acceptance are still needed.

## Regression and iteration history

The current DRAM and RTC host configurations each pass 64 groups under
ASan/UBSan. They retain the previous protocol tests and cover deferred
events, a genuinely concurrent blocked producer, bounded stop/retry,
startup/delete failures, full event queue and late events across restart.
The previous task source passes its original 60 groups with this harness.
Host timing/SDK seams do not establish native callback-stack margins.

An added interleaving test first fails on the preceding scheduler: an old
event enqueues HTTPD work while a newer post fails, and an unconditional
rollback forgets that pending work. The conditional rollback correction
retains the HTTPD reservation. The original assertion log, exact preceding
core and fixture are preserved. Two separate omission controls still fail
at their intended stop-drainage and duplicate-work assertions.

All three preceding scheduler images completed full HE-AAC with zero
allocation failures before that interleaving test was added. Their original
reports are retained under `before-post-rollback`; those passes do not
qualify the missing interleaving behavior. The first Clang comparison also
found one multiplication-width warning. The explicit 64-bit period fixes
it; the final normal-PDM Clang run completes 53 units with zero errors and
the same 100 previously reviewed warnings. The original comparison and
source iteration are retained separately.

[Observed outcomes and byte bindings](observed.json) preserve all seven
terminal runs, UART and RTC-access proofs. `code_commit` names the committed
implementation at packaging time; the diagnostic manifests' older workspace
HEAD describes their pre-commit build context. Exact source bytes bind those
builds to the recorded implementation. Earlier source snapshots are clearly
separated from current source. Private keys, full flash, diagnostic images,
ELF/map and raw compiler output remain local under ignored `.build`.

Reproduce with the [OpenETH instructions](../../target/cyd_full_app_openeth_qemu/README.md)
and `--codec aac --aac-profile he --through-eof --full-tls-records --websocket-clients 2`,
using a fresh output directory. The preserved continuous-DAC timeout,
normal production exports and physical Wi-Fi/audio/RTC timing remain open.
