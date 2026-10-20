# CYD permanent network owner execution

```text
python tests/run-cyd-network-runtime.py --out .build/cyd-network-runtime-01 --tsan
```

The runner freezes all sources and headers before compilation. It compiles the
complete production owner, checked netif helper, native state and shared Wi-Fi
store translation units. Network state publication and shared erase execute;
unrelated state/store functions are not qualified by their compilation alone.
The real owner task runs on a pthread. Its actual `vTaskDelay` boundary parks
between steps while tests drive a virtual clock. A blocked reservation barrier
also permits modeled SDK latency; separate cases inject invalid negative or
saturated clock values. Queues, mutexes and
event groups use pthread synchronization. Tests call the actual registered
callbacks and public APIs; no test writes an owner phase, private state or ACK.

Wi-Fi, netif, task creation, event registration and SNTP notifications are
controlled SDK seams. The active table is supplied directly; parsing and desired
storage are qualified separately. `wifi_config_t` and SDK event structs are
field models, not target ABI replicas. Requested owner priority/core/stack and
queue capacity are checked, but pthread scheduling/stack memory does not model
the ESP32. Actual FreeRTOS scheduling, RF/channel changes, TCP portal delivery,
target memory/HWM and physical audio or power effects remain separate gates.

Each case is a fresh process. Eighty-two cases exercise the real loop: immutable
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

The shared generation-aware power component executes in full. SDK power calls
must originate from the real owner thread. Cases preserve audio intent accepted
before Wi-Fi startup, reject old receive/finish after a new command (including
generation wrap), reactivate the same generation on receive retry, and check
the three-attempt/250 ms failure budget and coherent desired/applied diagnostics.
An SDK call barrier admits a newer command while the old call is blocked; its
success or error cannot charge the new revision, and the next owner step
reconciles the current intent. The critical-section seam is a pthread mutex;
hardware power draw and real RTOS scheduling are not measured.

N5 desired settings are a coherent committed RAM API seam. The actual NVS writer
and strict HTTP parser run in their separate suites; this owner campaign does
not claim an actual NVS/HTTP/owner interleaving. The full hostname setter caller
and SDK return handling execute: initial configuration must precede driver
start, subsequent setters require checked disconnection, online edits remain
pending without disconnect, identical names avoid another allocation, and a
blocked setter records the captured old hostname while newer settings remain
desired. The pinned SDK's OOM fallback to `espressif` is modeled and must clear
the old configured-value validity. It is netif configuration, not DHCP server
acceptance or mDNS.

AP timeouts run in the existing owner loop, with no added task or timer. Zero
disables admission. Tests cover exact one/30-minute boundaries, live AP enable
failure, timeout edit/disable, hostname-only edit, online cancellation, late
link loss and manual-cycle rearm. Association waiting for DHCP, netif up,
nonzero stale IP, SDK errors, an in-flight callback before queue publication,
and changes during SDK query/reservation all suppress expiry. At expiry the
real owner calls the reboot service through a lease seam; it never requests an
ordinary queued reboot. Held/failed OTA admission gets a fresh full interval
after return, including a blocked slow reservation. Releasing the held lease
cannot trigger an old pending AP restart. After reservation, current settings,
link, manual admission and stopping lifetime are checked again before calling
the immediate restart API. The actual lease service is qualified separately.
The restart double returns with its reservation held; production `esp_restart`
does not return. The owner cancels that returned test lease and rearms to avoid
an immediate repeated decision. Unrepresentable INT64 deadlines suppress a
premature restart, and negative clocks cancel admission. The last successful
eligibility check is the application arbitration boundary: an SDK/RF event or
settings save arriving later cannot be atomically excluded by the restart API.

Twelve exact test-only production mutations must fail the intended semantic
assertion: failed-config publication, pending-event stale status, AP teardown
during manual retry, obsolete RSSI retention, missing power polling and reversed
Wi-Fi power modes, OOM retaining hostname validity, a stale setter claiming the
new desired hostname, missing final AP guard, using the ordinary reboot queue,
omitted netif proof, and rearming from a stale pre-call timestamp. Crashes, sanitizer failures
and timeouts do not count as mutation detections.

ASan/UBSan are mandatory. Optional TSAN first runs an independent race-free
pthread control to distinguish an unavailable environment from a clean race
check. Source hashes, commands, raw logs and explicit results
are retained in the new output directory. `--case NAME` selects a partial
campaign and labels it incomplete. No board is accessed or flashed.
