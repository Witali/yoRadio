# CYD hostname and optional AP timeout: N5 software qualification

Implementation: `a7012415d4dbbdfffe6db50c0cc7f4e09df6ef5b`, including the
focused immediate-restart prerequisite `de1fa7a3a`. This records software
qualification; the complete transfer and physical gates remain open.
SDK application exports are recorded separately. This README becomes immutable
when an exported firmware manifest binds its hash.

The existing NVS settings module is now initialized after NVS, registered in
CMake and connected to the permanent network owner and native WebUI. Defaults
are DHCP hostname `yoradio` and AP timeout `0` (disabled). Hostname is one ASCII
label of 1–23 bytes; timeout is 0–30 minutes. Persistence publishes only after
successful NVS commit. Failed initialization leaves settings HTTP unavailable;
ordinary networking may use clearly identified local defaults.

The initial hostname is configured before Wi-Fi starts. Later changes are
applied only at a checked disconnected connection attempt; saving a form never
forces an online disconnect. The snapshot distinguishes desired settings from
the last successful netif configuration. It does not claim DHCP server
acceptance or mDNS. Pinned SDK hostname OOM can discard the previous string;
that result invalidates the old configured-hostname success.

The AP timeout uses the existing 100 ms owner loop and an absolute deadline.
Online, disable and stop cancel it. Timeout changes, connection-cycle changes
and a fresh offline AP interval rearm it; hostname-only edits retain the interval.
Expiry requires AP_IDLE with no active/pending cycle, exact SDK NOT_CONNECT,
netif down, a successful zero-IP query, current settings and unchanged
link/lifecycle evidence. The owner reserves the existing reboot service and
checks eligibility again before immediate restart. It never inserts an ordinary
durable pending AP reboot. Blocked eligibility or lease admission starts a fresh
whole interval, so failed OTA cancellation cannot release an expired AP request.
An unrepresentable full deadline does not authorize an early restart.

The final successful check is the application arbitration boundary. The SDK
cannot make an RF event or settings command arriving afterward atomic with
`esp_restart`. The immediate path retains its reservation across the SDK call
outside the portMUX; the original committed-credentials/OTA reboot semantics
remain intact. Existing task affinity, priority, stack and board pins are unchanged.

| Gate | Evidence |
| --- | --- |
| Complete actual network owner and callbacks | [82 cases + 12 exact semantic controls](owner/report.json), strict warnings and ASan/UBSan |
| Complete settings module/NVS seams | [12 cases + 7 controls](persistence/report.json), concurrent save/init and commit failures |
| Complete HTTP handler + actual settings/NVS source | [8 groups, 80 checks, 8 parsed JSON responses + 7 controls](http/report.json), ASan/UBSan |
| Actual page script | [48 groups + 14 controls](page/report.json), Node DOM/fetch/WebSocket seams |
| Actual reboot API | [CYD 208 ordinary + 208 immediate cases; unchanged C3 208 ordinary cases; 4 controls](reboot/report.json), real competing threads and SDK-entry barriers |
| Startup and existing core bindings | [29 groups + 9 controls](startup/report.json), actual app/facade bodies |
| HTTP route setup and rollback | [All 23 HTTP registration failures, 24 slots including WS + 5 controls](web-start/report.json), actual startup/capabilities/static functions |
| Existing network HTTP and WebSocket regression | [16 cases + 4 controls](network-http/report.json), [58 WS groups](websocket/report.json) |
| Full actual SDK Clang AST | [52 units, 86 warnings, 0 errors](lint/report.json); all 652 source/header/build inputs frozen before analysis and verified afterward |
| Independent read-only review | [Review](review/review.json): one reproduced stale timer-label defect resolved and independently rechecked; no remaining actionable finding in the recorded scope |

The five diagnostics added to the prior 81-warning baseline are explicitly
[triaged](lint-triage.json): intentional nonzero string/binary comparisons and
a binary NVS magic flagged as a non-terminated string. No warning is suppressed.
Clang AST success is not optimized Xtensa code-generation evidence.

The settings HTTP API has GET/POST `/api/native/network-settings`, a strict
192-byte query limit and exactly two complete fields. Nonempty bodies close the
session with handler failure, preventing HTTPD body purge. Desired persistence,
configured hostname, application pending, runtime errors and AP countdown are
reported separately. The UI protects dirty edits and successful saves from old
GET responses, serializes forms with uploads/OTA and invalidates an old countdown
label when a post-save refresh fails.

The owner binary uses coherent settings-RAM and reboot API seams. Actual
settings/NVS and actual reboot arbitration are qualified by separate gates;
this is not a claim of one cross-layer RF/HTTP/NVS/OTA execution. No board was
flashed or reset. Physical DHCP/AP-channel behavior, RF losses, actual restart,
OTA/flash durability, SMP scheduling, heap/DMA/stack/power and long playback
remain unqualified. No clean TSAN claim is made.

[qualification.json](qualification.json) binds original reports and current
source checks. [archive-paths.json](archive-paths.json) maps relocated raw inputs
to short content-addressed files, including every lint manifest input. The root
manifest covers all archived bytes except itself. Earlier frozen archives and
versioned releases are unchanged.
