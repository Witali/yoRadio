# ESP32-C3 production health endpoint

`GET /api/native/health` exposes numeric runtime evidence in quiet builds,
without enabling the console, periodic logging or a sampler task. It uses
the same local HTTP service as the existing native playback API. The reply
has `Cache-Control: no-store` and contains no station, Wi-Fi, credentials,
memory addresses or certificate data.

| Field | Meaning |
| --- | --- |
| `schema` | Schema version, currently 1 |
| `boot_id` | Random 64-bit session identifier as 16 hexadecimal characters, initialized before HTTP starts |
| `uptime_ms` | Milliseconds since boot, from the 64-bit ESP timer |
| `reset_reason` | ESP-IDF reset-reason enum value |
| `heap` | Current free bytes with `MALLOC_CAP_8BIT` |
| `largest` | Largest allocatable block with that capability |
| `minimum_heap` | SDK heap low-water measurement for that capability |
| `tasks` | Current FreeRTOS task count |
| `allocation_failures` | Lifetime failed-allocation callbacks since `cpu_profiler_start()` registered the hook |
| `task_watchdog_events` | Lifetime task-watchdog ISR notifications; zero if task watchdog is compiled out |

Heap and task values are sampled on demand; they are not an atomic snapshot
of every task. Heap samples include the HTTP request's own allocations.
Compare settled observations made through this same endpoint, rather than
equating them with UART samples taken under a different request load.

The existing allocation-failure callback retains its diagnostic log when
profiling is enabled and also increments the counter. Quiet builds register
only the counter callback. Both error counters are in internal RAM; their
quiet callbacks are in IRAM. The allocation counter preserves the previous
interrupt mask around its increment on the single-core C3. There are no heap,
log or timer calls in that callback. The watchdog has one ISR writer.
Successful allocations and successful decoder operations do not update these
counters. Boot identity plus both counters use 16 bytes of static state.

## Acceptance scope

`tools/esp32c3_tests/production_health.py` rejects missing/invalid fields,
changed boot identities, decreasing uptime, allocation failures and watchdog
events. It retains the offending observation before raising. `HealthBoard`
adds one health request after every status request; timing includes both
requests. Create a new monitor after a deliberate reboot or OTA.

The endpoint does **not** measure PCM accuracy, DMA underruns, analog sound,
CPU utilization or every decoder/TLS error. Continue to verify format, EOF,
network recovery and audio delivery separately. Silence in a quiet UART log
must never be interpreted as proof that all runtime errors were absent.

## Checks

```powershell
python tests/test-production-health.py
python tests/test-production-health-native.py
```

The native test compiles the actual quiet callback and HTTP handler bodies
with SDK doubles under ASan/UBSan, with the watchdog enabled and disabled.
It checks callback registration errors, fault accumulation, interrupt-mask
restoration and maximum-width JSON values. It does not simulate hardware
interrupt timing. The firmware ELF audit separately verifies both callbacks'
IRAM placement and absence of the optional profiler state/task.
