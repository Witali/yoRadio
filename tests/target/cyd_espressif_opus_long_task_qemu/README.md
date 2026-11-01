# Actual CYD tasks with long Opus packets and real resizing

This sibling compiles the unchanged complete production audio service, state,
health and registration, with real ESP-IDF queues, tasks, allocators and public
vendor decoder. HTTP transport and output/LED hardware remain explicit seams.
No physical board, external network or private codec ABI is used.

The full legal 120 ms fixture is 707097 bytes. The strict reference is the
completed fragmented-input resize campaign: all original native command logs,
compiler/image/child/source bindings and measured raw PCM identity are rechecked
before generating reference.h. Raw output is 2119680 PCM16 stereo bytes,
SHA 670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684.
Required Opus pre-skip/end trimming remains separate and unresolved.

Cases preserve actual T0 ordered EOF, T1 partial Stop/discard/reopen and T2
partial three-owner maintenance with token-checked resume. Full PCM, metadata,
all public client/decoder cleanup and original task bindings are checked:
stream core 0 / priority 3 / stack 6144, decode core 1 / priority 5 / stack 16384,
output core 1 / priority 6 / stack 4096. Watchdogs, assertions, heap poisoning
and stack canaries remain enabled.

The public process wrapper observes every initial capacity, real buffer error,
following retry and close. It never modifies vendor arguments or application
control state. Each observed resize must show capacity 12288, needed 23040,
zero consumed/decoded bytes, and an immediately following real call at 23040
with unchanged input arguments. Totals are counted from actual records rather
than supplied as assumed success values.

```text
python -B tests/run-cyd-espressif-opus-long-task-qemu.py --reference .build/<passing-fragmented-resize-campaign> --output .build/<fresh-task-campaign>
```

The pinned reviewed common task controller retains actual compiler dependency
closure and before/after source/tool/image checks. Historical completed targets
are unchanged. This diagnostic does not qualify real HTTP/TLS/TFT resources,
deliberate backpressure, output-allocation failure, physical audio or universal
Opus conformance. Images remain local and must not be flashed as radio firmware.
