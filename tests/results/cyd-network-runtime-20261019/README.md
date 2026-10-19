# CYD network profiles, reconnect and checked signal state

Source slice: `b736d38f`, with separate loader, checked-netif and test commits.
N0–N3 of the [network design](../../../docs/CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md)
are implemented. N4 generation-aware audio power and N5 hostname/AP timeout
remain open. Existing task affinities and board wiring are preserved; the new
network owner has priority 2, core 0 and a 4096-byte stack budget.

| Gate | Frozen evidence |
| --- | --- |
| Historical CYD/C3 defects | [Baseline](historical-baseline/report.json): eight intended assertion failures and one limited bool-power characterization, exact historical `048a5c42` bodies |
| Atomic first-five valid boot profiles | [Loader](profiles/report.json): 44 groups and seven semantic controls; actual reader/recovery/file transaction and mapped stdio |
| Checked netif creation and retained cleanup | [Netif](netif/report.json): 35 groups and six semantic controls; selected actual pinned SDK attach/default-handler/clear bodies with explicit allocation/event seams |
| Complete permanent owner loop | [Owner](owner/report.json): 44 cases and four semantic controls; actual task, callbacks and public APIs execute with pthread queues/mutexes and deterministic SDK/clock seams |
| Network GET and reconnect admission | [HTTP handlers](http/report.json): 16 cases, seven parsed actual JSON responses and four semantic controls |
| Deferred status publication and RSSI validity | [WebSocket](websocket/report.json): 58 fixture groups, actual production status/transport core; maximum JSON 4899 of 5120 bytes |
| Static workers, route rollback and page | [Static/page](static-page/report.json): all 21 HTTP route failures, worker ownership, four controls and 38 Node DOM/fetch/socket cases |
| Existing desired persistence | [Persistence](persistence/report.json): 46 groups and two controls, actual current loader/store functions |
| Physical row bounds and read/close failure | [Reader](physical-row-reader/report.json): 29 groups plus an explicitly historical old-reader negative |
| Current facade, app startup and retained affinities | [Startup](startup-time-affinity/report.json): 28 groups and eight semantic controls, including checked startup failures and event-loop ownership |
| Xtensa GCC with pinned ESP-IDF v6.0.2 | [Component logs/configuration](sdk): main library compile passed; final incremental log records the last web service rebuild |
| Full CYD vendor clang-tidy and focused custom FLAC AST | [Vendor](lint-vendor/report.json): 49 units, 81 warnings, zero errors; [custom](lint-custom/report.json): two units, one warning, zero errors |

Host C campaigns use ASan/UBSan. The whole-owner campaign uses strict compiler
warnings as errors; SDK/RTOS/HTTPD boundaries are stated in each runner/report.
No sanitizer error, compiler failure or timeout is counted as a detected semantic
mutant. The independent race-free TSAN control fails during runtime startup
(`unexpected memory mapping`, with one empty-output failure), so no clean TSAN
or proven SMP-safety claim is made.

Clang-tidy freezes and rechecks 639 vendor and 441 focused-custom inputs.
Compared with the previous 46-unit/77-warning campaign, the four extra warning
instances are three range-preserving RSSI conditional conversions and one
`memcmp` padding caveat in the expanded WS status key. The key is initialized
before capture, but universal padding-byte stability after structure assignment
is not guaranteed; unnecessary sends on other compiler behavior remain a
portability caveat. No unsafe access or malformed payload was reproduced.
No warnings were suppressed. See [triage](lint-triage.json).

The first five valid profiles are immutable until reboot; desired edits do not
change the active cache. There are at most three attempts per profile, 20 seconds
per attempt and 300 seconds per cycle, including overhead. A cycle deadline may
truncate its final attempts. A permanent owner handles late outages, wrap,
manual-cycle admission, APSTA retention, event overflow and ambiguous old SDK
events. A snapshot masks old IP/RSSI while link notices await reconciliation.
RSSI validity and AP state are independent, and the page rejects stale REST
responses arriving after newer WS link notices.

The source snapshots, generated units, compiler/test diagnostics and reports are
preserved. Current input hashes were checked against all host snapshots except
the explicitly historical Git sources and the original generated netif-test
configuration, which is preserved with its original hash. The current SDK
configuration adds only the default vendor FLAC selection macro and is archived
separately. SDK source snapshots were collected after
the component compilation; this is not a frozen full application reconstruction.
See [qualification](qualification.json) and [raw-byte manifest](manifest.json).
No test executables, live Wi-Fi credentials or private keys are included.

Full application links/exports, custom FLAC execution in QEMU, RF outage/DHCP/AP
channel behavior, real TLS/audio concurrency, hardware heap/stack/watchdog and
power measurements remain open. These host results do not demonstrate physical
radio behavior, target ABI or real-time performance. No Wi-Fi buffer reduction
or C3 resource measurement is transferred to CYD by this change.
