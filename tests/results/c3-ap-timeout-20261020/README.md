# C3 AP timeout repair qualification

Implementation: `0f484bbc8ad6225aa80be35457b2c4f195b77678`, with immediate
reserved restart API from `9cc619778148b5111a629f64388a51a445f25178`.
This is a donor repair discovered while transferring CYD network settings.
The already qualified CYD implementation is unchanged.

The old C3 AP timer called `esp_restart()` directly, including while OTA held
its restart lease, after late GOT_IP, or after a successfully saved timeout of
zero. All three behaviors are reproduced from exact Git revision `1256de595`
using its actual startup/AP callback and complete settings source. Each fails
its named safety assertion with exit 42; generic crashes do not count.

The repair removes the timer and gives the existing 100 ms RSSI/power task sole
ownership of the deadline. RSSI remains at 2 s, priority 2 and its existing
2048-byte stack. No new task or target affinity change is introduced. AP delay
remains optional, default 0, range 0–30 min, with unchanged NVS namespace/key.

Accepted settings saves serialize, commit first and then publish one packed
32-bit value/revision. Same-value saves and rapid disable/re-enable invalidate
old deadlines. Exhausted revision rejects before NVS writes. Restart requires
current APSTA/unassociated/down/zero-IP observations, unchanged operation and
settings revisions, activity admission, an exact reboot reservation and a final
live recheck. A pending asynchronous connect first needs checked cancellation;
it cannot restart in that iteration and needs a fresh full interval. Failed or
held admission creates no ordinary pending reboot. Later RF/config events after
the final application arbitration boundary cannot be atomically excluded by
the SDK restart API.

| Qualification | Result |
| --- | --- |
| Actual AP network spans + complete settings/NVS unit | 42 cases, 8 exact semantic mutants, 3 historical defects |
| Complete actual reboot/lease implementations | 416 CYD + 416 C3 scenarios; 8 exact controls |
| Shared power + actual C3 RSSI/intent/sleep bodies | 16 cases, 4 controls |
| Complete C3 time settings unit | 69 checks, 3 controls |
| Actual CYD startup/facade and C3 guarded STA_START | 29 groups, 9 controls |
| Actual C3 credential persistence APIs | 43 scenarios |
| Actual C3 time adapter and timezone status | 14 groups, 6 controls |
| C3 WebSocket IO/session/framing | 5189 cases, 4 historical controls |
| Full pinned SDK Clang AST analysis | 65 units, 127 warnings, 0 errors; 758 inputs frozen before and verified after |
| Independent source/test review | No open actionable findings; final report bound to current inputs |

Host campaigns use strict compiler warnings and ASan/UBSan. AP tests include
restored valid/invalid NVS delay, 400 accepted concurrent commits with 2000
snapshots, commit failures, late events/settings/association, sleep, failed
queries/reservations, checked cancellation and clock boundaries. Revision
exhaustion uses an explicitly documented settings initialization seed; the
normal complete settings translation unit remains byte-exact production code.

The AP suite executes exact selected network spans, with SDK/netif, RTOS,
credential loading, activity, reboot and power seams. Reboot and power execute
their actual implementations in separate suites. This does not establish a
cross-layer hardware/RTOS proof. Existing power and bootstrap regression suites
explicitly model AP boundaries rather than silently expanding their claims.

All 127 Clang diagnostics match the previous N4 baseline by path, severity,
check and message, ignoring line shifts and generated overlay directory names.
The modified network/settings units have zero warnings; the reboot unit retains
its three previous warnings. Existing warnings are not suppressed or declared
fixed. No TSAN result is claimed.

`qualification.json` binds the original reports. `manifest.json` binds every raw
archive file; `archive-paths.json` maps flattened long dependency paths. All 758
lint manifest inputs are included, including extensionless compiler flags.
Source/fixture snapshots, generated spans, commands, logs and exact failure
markers are preserved. Original reports are not relabeled as clean Git builds.

SDK application exports are documented separately in `SDK.md` once completed.
No physical board, serial flashing, reset or OTA was used. RF/DHCP behavior,
actual power loss, full-radio heap/stack margins and physical sleep/reboot timing
remain open. No production CYD performance or memory saving is inferred.
