# Native time and private Wi-Fi transfer qualification

2026-10-18. Software checkpoint for the time/settings and desired-credential
parts of CYD-C3-09. Runtime profile rotation, reconnect/AP supervision, RSSI
and generation-safe power policy remain in the
[runtime design](../../../docs/CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md).
No board has been flashed or reset for this campaign.

| Scope | Frozen evidence |
| --- | --- |
| Shared SNTP backend | [Final report](time-backend-final/report.json): 82 actual groups across both pinned SDKs and capacities 1/2; 18 targeted semantic controls. Actual full SNTP core, managed lifecycle and DNS enqueue execute; UDP/RTOS/TCPIP scheduling and wall clock have explicit host seams. |
| CYD settings and time worker | [Report](time-cyd/report.json): 24 cases and seven semantic controls. Actual NVS codec, commit/publication, worker, revisions, offline startup, clock conversion, retry and sync state. |
| C3 coherent time settings | [Report](time-settings-c3/report.json): 69 checks and three semantic controls. Concurrent setters commit before publishing the coherent RAM snapshot. |
| C3 adapter and worker | [Report](time-service-c3/report.json): 14 groups and six semantic controls. The existing OLED/RTC/deep-sleep behavior is outside this transfer. |
| C3 borrowed-name lifetime | [Current report](time-lifetime-final-c3/report.json): actual current adapter/new backend preserves a DNS-borrowed name before enqueue; historical production `642ee17f` detects corruption before the queued stop acknowledgement. Actual pinned SDK wrappers/SNTP/DNS execute. Earlier successful snapshots remain separately preserved. |
| CYD startup and station events | [Report](time-startup-events/report.json): 32 groups and nine targeted semantic controls. Real startup/event function bodies retain display/network affinity, defer network work until IP, invalidate lost IP and reject use of retained driver credentials without a selected file profile on both targets. |
| CYD time HTTP | [Report](time-http-cyd/report.json): 69 checks in seven groups, five semantic controls and three parsed actual JSON responses. Query decoding and real NVS save/load execute; service snapshots and HTTP response/cleanup are seams here. |
| CYD time over TCP/TLS | [Report](time-wire-cyd/report.json): 23 real TCP cases and 23 CA/hostname-verified native TLS cases, plus two exact SDK-purge controls. Actual SDK parser, URI dispatch, session lifecycle and production time handlers execute; time-service snapshots, NVS and SDK field/RTOS models remain explicit seams. |
| Shared desired Wi-Fi store | [Report](wifi-store/report.json): 2,624 groups, 320 real pthread edits, 65 wiped private workspaces and five semantic controls. Actual store/file transactions execute with synthetic credentials and injected failures. |
| Strict Wi-Fi JSON decoding | [Report](wifi-json/report.json): 2,445 groups, 20,000 malformed probes and four semantic controls. Duplicate/escaped aliases, unknown fields, Unicode, limits and partial-secret erasure are covered. |
| C3 desired-store integration | [Report](wifi-store-c3/report.json): 43 scenarios, two exact historical-source controls and one active-cache control. A durable edit changes next-boot desired storage; the running station cache stays unchanged. |
| CYD desired-store integration | [Report](wifi-store-cyd/report.json): 46 groups and two semantic controls. [Boot reader](wifi-reader-cyd/report.json): 28 fixtures and an exact historical reader control. Empty live storage does not resurrect stale backup credentials. |
| Shared HTTP I/O and private endpoint | [Report](wifi-http-io/report.json): CYD70/C380 groups and five semantic controls per target; 63 whole allocations wiped per variant. Actual pinned SDK buffered receive/send/session/context paths cover pending bytes, WANT direction, timeouts, stale edits, response failure and foreign ownership. These are field-model seams, not whole-network evidence. |
| Final metadata/edit/import handlers | [Report](wifi-http-final/report.json): CYD97/C3107 groups, eight semantic controls and 88 wiped allocations per target. All three legacy imports use the small shared request I/O context, reserve reboot before any live publication and still commit reboot after a durable Wi-Fi save when sending the response fails. |
| Existing import compatibility | [Uploads](legacy-uploads/report.json): CYD69/C368, CYD reboot10 and paired-file105 scenarios. [Multipart](multipart-final/report.json): 896 header cases, five real C3 receive variants and the current OTA246 cases. Actual source functions run with the documented filesystem/RTOS/SDK seams. |
| Wi-Fi over TCP/TLS | CYD [HTTP](wifi-wire-cyd-http/report.json) and [TLS](wifi-wire-cyd-tls/report.json), C3 [HTTP and TLS](wifi-wire-c3/report.json): 31 cases per board/transport, 124 total. Actual pinned HTTPD parser/session, credential owner, JSON, all three legacy imports, private-path admission and worker bodies execute together. Real 10-second idle and 30-second overall deadlines, paused senders, response OOM and reboot-after-durable-save are covered. The exact terminal-return control detects the real SDK entering request deletion and two body-purge receives. |
| C3 route startup | [Report](web-start-c3/report.json): actual startup function runs against controlled HTTPD/RTOS seams, including every registration failure and retained ownership when shutdown fails. |
| CYD routes and static workers | [Report](web-start-static-cyd/report.json): all 20 HTTP registrations, rollback, activation, both private-path boundaries, raw/gzip/playlist serving and four semantic controls. Methods and aliases are rejected before asynchronous admission or file open. The same frozen campaign also executes all 35 compact-page groups. |
| Compact CYD interface | [Report](web-page-cyd/report.json): 35 Node groups and eight semantic controls. First-row edits preserve the remaining rows, `keep` preserves private/legacy bytes, open networks require an explicit action, and stale time responses cannot overwrite a completed save. Existing OTA flows remain covered. |
| Existing C3 WebSocket publication | [Report](ws-status-c3/report.json): 22 actual status-loop scenarios, seven semantic controls and 57 JSON-parsed TEXT frames. Pending buffers, admission retries, playlist events and the real fragmented-message deadline work execute together. HTTPD/session/frame I/O and RTOS stepping are seams; prior TCP/TLS qualification is separate. |
| Complete CYD clang-tidy | [Report](lint-cyd/report.json): 46 units, 77 warning instances, zero parse/tool errors. Every analyzed unit has an exact hash-verified source snapshot. |
| Complete C3 clang-tidy | [Final report](lint-c3-final/report.json): 64 units, 127 warning instances, zero parse/tool errors. Recovery preserves 61 completed original units, freshly runs two unfinished units and separately analyzes the newly registered Wi-Fi adapter. Original attribution is reconstructed and explicitly described; it is not presented as a complete original pre-analysis snapshot. |
| Build and client tools | [Production wrapper](production-wrapper/report.json): 42 cases passed; one Windows symlink case skipped. Old isolated configs gain only the required minimum SNTP capacity, failed replacement preserves the prior config and unsupported exports fail. [Supplemental clients/tools](clients/report.json): 73 Node and 16 Python cases pass. Architecture assertions supplement the separate executable C campaigns. |

All C campaigns above pass ASan/UBSan. Negative controls require the intended
semantic assertion/marker; sanitizer crashes, timeouts and unrelated process
failures do not count as detection. Test credentials are synthetic. The archive
contains source and report snapshots, not device credentials, CSV backups,
private keys, generated executables or firmware binaries.

The shared backend rejects enabled foreign clients, foreign names and disabled
numeric-IP-only slots before managed allocation or rebinding. This is a
sole-owner contract; it does not atomically exclude another component that
ignores the contract and invokes raw SNTP APIs concurrently. DNS generation
cancellation is not implemented. Actual assertion-enabled SDK UDP-PCB OOM
still aborts; the no-assert case is reported separately.

Wi-Fi metadata exports SSIDs and opaque row/revision identities only. Existing
passwords are resolved by `keep` inside the credential owner. A native metadata
failure never falls back to downloading `/data/wifi.csv`. Runtime selection
and desired-storage capabilities remain distinct: CYD currently uses the
first valid active boot profile, and advertises `wifi_profiles:false`.

The software HTTP/TLS and explicit CSV-import gates above are complete.
Final GCC image/configuration verification is recorded in [SDK.md](SDK.md).
Host tests do not qualify physical RF recovery, NVS/SPIFFS power loss, device
clock accuracy, heap/stack high water, DMA behavior or browser layout.

The Wi-Fi wire harness uses explicit host field layouts, foreground SDK session
stepping, an inline asynchronous/static queue and a synthetic filesystem with
SPIFFS rename semantics. Its late-publication case advances the host clock
after durable rename; idle and overall timeout cases use real elapsed time.
These tests do not establish target ABI, RTOS scheduling or physical flash
atomicity. Native TLS uses the pinned ESP-TLS/MbedTLS path and a CA/hostname
verified client; no hardware TLS or RF claim follows.

The pinned HTTP parser waits for a first body byte before dispatching a request
whose Content-Length is nonzero. Rejection tests therefore leave 1 MiB minus
one byte unread after that byte; handler budgets do not cover the SDK's earlier
receive wait. Raw TCP can reset after a complete rejection response when unread
input remains. TLS tests require proper close_notify. Changing a time rejection
to return ESP_OK causes the actual SDK to purge the one pending body byte;
both targeted controls detect that exact behavior without relying on a timeout.

The [warning review](lint-review/report.json) and JSON bounds investigation
retain the original reports and exact helper probes. The apparent C3 JSON
overrun has an infeasible analyzer
path and a valid capacity invariant; 416,784 additional synthetic boundary
checks pass ASan/UBSan. No production rewrite or warning suppression was used.
Existing AAC owner-view work remains deferred. Experimental Xtensa Clang20.1.1
optimized code generation crashes in `time_settings_valid` with a vector
instruction selection failure; its AST analysis succeeds. Production images
use the pinned GCC compiler, with separate integrity checks below.
