# Coverage and limits

The service gate compiles the whole production `native_input_reclaim.c` and the
canonical `adaptive_input.c` with explicit libc/heap-accounting, SDK calloc and
pthread RTOS seams. Public APIs drive 21 cases and 17 exact semantic controls;
private runtime registry or queue state is not seeded. The service tests model
allocation failure and recovery, not actual SDK OOM. A 10000-packet concurrency
case checks FIFO/lease behavior within the host model.

Coverage includes original-allocation-first delegation; successful, malformed,
zero, overflow and ISR results; unbound state; repeated exhaustion and minimum
floor; release/free before retry; fixed target-minus-minimum retry budget during
refill; protected WRITING/READY/READING/control storage; wrong-owner/idempotent
bind; pinned detach, retirement admission, explicit retry, and drained pins.
The representable pin-count overflow guard is source-reviewed; the tests do not
create SIZE_MAX real pins or write private registry values.

The startup gate retains the old allocation/task/codec-registration failures,
rollback/retry, notification gate, concurrent/reentrant callers and permanent
output initialization. Four codec combinations run with ring input, adaptive
input without reclaim, and adaptive input with reclaim: 12 configurations. The
actual reclaim module links into enabled variants, and a linker-wrap bind spy
checks READY publication, the real encoded pointer and zero prior notifications.
Failed pre-READY startup does not bind. Allocation-time TLS probes before bind
delegate exactly once without reclaiming. A foreign-owner collision leaves
READY/tasks and accepted Play requests intact, only logs a warning, retains the
foreign pool, and makes later hook pressure reclaim the foreign pool only.
Fixture teardown joins all ordinary owner threads, publicly detaches, then uses
test-only production discard; it is not a new runtime teardown API.

The startup SDK allocator is a deterministic failure seam. Its
`observe_health_failure` callback and one-registration/identity checks are also
explicit SDK failed-allocation callback seams. They do not execute actual
`native_health.c`, establish SDK heap-failure integration or prove a real TLS
handshake. The reviewer authored this startup suite; its evidence is identified
separately from the independently authored production-service/root-wiring review.

The CMake gate checks enabled, disabled, early expansion and five invalid
prerequisites. Disabled/early cases preserve prior options and add no module or
wrapper. Enabled configuration appends the precise module/wrap/retention options.
Kconfig defaults the feature off and requires adaptive input, internal mbedTLS
allocation and recoverable allocation failures. These are configure checks,
not a final ESP32 link or SDK execution gate.

Historical startup attempt01 failed because the newly frozen include closure
omitted transitive `stream_tags.h`. Attempt02 failed on pre-existing stale
fixture seams for `ESP_ERR_TIMEOUT` and `native_audio_output_request_pause`.
Both are preserved as failed preparation attempts; neither is counted as a
successful or production defect. Final attempt03 is authoritative.

Full opt-in Clang completed 54 units with 86 warnings and no errors. All 661
source/header/configuration inputs were frozen before analysis and checked
afterward. The new reclaim unit has zero diagnostics. Comparison with the prior
telemetry 53-unit/86-warning report preserves unit, logical diagnostic file,
severity, check, full message and multiplicity while normalizing worktree/HTTPD
build paths and ignoring line/column offsets. The exact multiset delta is empty.
This is an unchanged-warning result, not a warning-free-code claim or optimized
Xtensa code-generation result.

The independent review reads the production service and root startup/CMake/
Kconfig wiring, canonical queue and pinned SDK 6.0.2 allocator/context contracts.
It verifies owner/pin/retirement lifetime, original-first behavior, lock order,
bounded retries, no global allocator/free/failed-callback replacement and no
post-READY rollback. Current Stop/EOF/maintenance do not destroy the successful
pool. Public DETACHED drains allocator pins only; ordinary producer, consumer,
restore and health users must separately quiesce before future destruction.
The original SDK allocator is still called first even in invalid/ISR contexts;
the wrapper does not certify the original allocator as generally ISR-safe.

The raw reports and hash checks establish these host/static/source-review
results. They do not establish actual SDK OOM, ESP32 scheduler behavior, final
wrapper/link resolution, physical interrupt latency, cache/IRAM execution,
TSAN, real heap fragmentation recovery, TLS/RF/DMA behavior, resource margins,
audio quality or performance. No test was rerun and no SDK build, flash, serial,
physical I/O or network download was performed to assemble this archive.
