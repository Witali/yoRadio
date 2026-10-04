# ESP32-C3 network memory diagnostics

`CONFIG_YORADIO_NETWORK_HEAP_PROFILE=y` is an optional diagnostic for the
physical ESP32-C3 firmware. It requires `CONFIG_YORADIO_CPU_PROFILE_HTTP=y`
and is **off by default**. It does not change AAC storage or decoding.

The HTTP profiler posts one persistent callback message to the lwIP TCPIP
thread, at most once per five-second profiling interval. Only that owning
thread walks the TCP lists and segment queues. The callback records:

- Free/used 8-bit heap, largest free block, allocated/free block counts.
- Active, TIME_WAIT, bound and listening TCP control blocks.
- Unsent/unacknowledged transmit segments and out-of-order receive segments.
- Snapshot sequence, age, callback duration and missed callback attempts.

No new task or task stack is allocated. One lwIP callback message remains
allocated until reboot; the same message is never posted twice while pending.
Allocation/queue failures are reported and can be retried on the next poll.
The callback copies counters under a short critical section and never logs
while on the TCPIP thread. Logging happens on the existing HTTP task.

## Interpretation limits

The log line is `PERF NET_HEAP: seq=... age_ms=... heap=... largest=...`.
The HTTP task logs the preceding snapshot, normally about five seconds old.
**Subtract `age_ms` from the host log-receive timestamp** when assigning the
sample to a playback window. Serial/host scheduling delay remains an error
source. `walk_us` includes scheduling interruptions; it is elapsed time,
not isolated CPU time.

TCP segment bytes are logical queued payload, **not unique allocated RAM**.
They exclude Wi-Fi driver buffers, TLS buffers and application receive queues.
Heap regions are inspected sequentially; unrelated tasks can allocate/free
between those reads. These counters can narrow a hypothesis but cannot assign
every allocation to a component or prove that RSSI caused a failure.

The pinned lwIP implementation keeps the static callback message after calling
it. Its heap-backed TCP PCB allocator still enforces the configured limit of
16 and can reclaim old TIME_WAIT entries. Do not infer unbounded PCB growth
from `MEMP_MEM_MALLOC=1` alone.

## Run and analyze

Use an awake physical build with the flag enabled. Save its exact `app.bin`
and adjacent `sdkconfig` in `firmware/development/<variant>/` before installing.
The existing public-stream runner verifies the installed image hash and keeps
its original acceptance thresholds:

```text
python tools/esp32c3_tests/public_streams.py --board http://BOARD_IP --serial-port COM9 --firmware firmware/development/esp32c3-aac-network-memory/app.bin --case groovesalad-32-aac --seconds 300 --interval 0.1 --transport http --ffprobe ffprobe --output .build/c3-tests/network-http32
python tools/esp32c3_tests/network_memory.py --input .build/c3-tests/network-http32 --output .build/c3-tests/network-http32/network-summary.json
```

For the HTTPS comparison, use `--case groovesalad-64-aac --transport https`
and a **different output directory**. Run board-controlling suites sequentially.

The summarizer uses only explicit playback windows and reports 30-second bins.
It retains the original acceptance object unchanged. Stale snapshots,
sequence gaps, changed missed-callback counts, callback warnings, and missing
intervals make network metrics incomplete; they never turn a failed playback
test into a pass. Raw samples remain available for inspection.

## Regression tests

```text
python tests/test-esp32c3-network-memory.py
python tests/test-network-heap-native.py
```

The first command checks delayed-window attribution, incomplete/invalid data,
missed callbacks and unchanged failed acceptance results. The second compiles
the actual C sampler with GCC and AddressSanitizer/UndefinedBehaviorSanitizer
(WSL GCC on Windows). It exercises callback lifetime, duplicate-poll prevention,
allocation/post failures, queue snapshots and thread/lock restrictions. It also
links the disabled header without lwIP or FreeRTOS dependencies. Missing GCC
is a skipped native check, not a successful compilation.

Hardware results and overhead are recorded separately in
[the 2026-10-04 measurements](ESP32C3_NETWORK_MEMORY_20261004.md).
