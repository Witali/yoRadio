# CYD permanent network owner execution

```text
python tests/run-cyd-network-runtime.py --out .build/cyd-network-runtime-01 --tsan
```

The runner freezes all sources and headers before compilation. It compiles the
complete production owner, checked netif helper, native state and shared Wi-Fi
store translation units. Network state publication and shared erase execute;
unrelated state/store functions are not qualified by their compilation alone.
The real owner task runs on a pthread. Its actual `vTaskDelay` boundary parks
between steps while tests drive a monotonic virtual clock. Queues, mutexes and
event groups use pthread synchronization. Tests call the actual registered
callbacks and public APIs; no test writes an owner phase, private state or ACK.

Wi-Fi, netif, task creation, event registration and SNTP notifications are
controlled SDK seams. The active table is supplied directly; parsing and desired
storage are qualified separately. `wifi_config_t` and SDK event structs are
field models, not target ABI replicas. Requested owner priority/core/stack and
queue capacity are checked, but pthread scheduling/stack memory does not model
the ESP32. Actual FreeRTOS scheduling, RF/channel changes, TCP portal delivery,
target memory/HWM and physical audio or power effects remain separate gates.

Each case is a fresh process. Forty-four cases exercise the real loop: immutable
0/1/5-profile tables, bounded reconnect/wrap, 20-second attempt/startup and
300-second cycle budgets, late events and duplicate SSIDs, APSTA preservation,
manual admission before START and throughout its cycle, RSSI validity/age,
snapshots, event overflow, projection recovery, lifetime and startup failures.
Each checks final owned resource release, except the explicit permanently
poisoned netif cleanup case, which verifies intentional retention and rejects
all future cleanup/reinitialization. Allocation/registration/task failures and failed unregister
exercise actual production rollback and retained object paths. An in-flight
callback barrier holds a real API reference while stop reaches its local wait
deadline. The SDK unregister seam returns promptly: the test does not claim
that a real SDK event-loop unregister call has a bounded wall-clock duration.
Concurrent publishers and snapshots run alongside the real owner thread.

Four exact test-only production mutations must fail the intended semantic
assertion: failed-config publication, pending-event stale status, AP teardown
during manual retry, and obsolete RSSI retention. Crashes, sanitizer failures
and timeouts do not count as mutation detections.

ASan/UBSan are mandatory. Optional TSAN first runs an independent race-free
pthread control to distinguish an unavailable environment from a clean race
check. Source hashes, commands, raw logs and explicit results
are retained in the new output directory. `--case NAME` selects a partial
campaign and labels it incomplete. No board is accessed or flashed.
