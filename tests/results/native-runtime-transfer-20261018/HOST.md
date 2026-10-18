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
| Shared desired Wi-Fi store | [Report](wifi-store/report.json): 2,624 groups, 320 real pthread edits, 65 wiped private workspaces and five semantic controls. Actual store/file transactions execute with synthetic credentials and injected failures. |
| Strict Wi-Fi JSON decoding | [Report](wifi-json/report.json): 2,445 groups, 20,000 malformed probes and four semantic controls. Duplicate/escaped aliases, unknown fields, Unicode, limits and partial-secret erasure are covered. |
| C3 desired-store integration | [Report](wifi-store-c3/report.json): 43 scenarios, two exact historical-source controls and one active-cache control. A durable edit changes next-boot desired storage; the running station cache stays unchanged. |
| CYD desired-store integration | [Report](wifi-store-cyd/report.json): 46 groups and two semantic controls. [Boot reader](wifi-reader-cyd/report.json): 28 fixtures and an exact historical reader control. Empty live storage does not resurrect stale backup credentials. |
| Shared HTTP I/O and private endpoint | [Report](wifi-http-io/report.json): CYD70/C380 groups and five semantic controls per target; 63 whole allocations wiped per variant. Actual pinned SDK buffered receive/send/session/context paths cover pending bytes, WANT direction, timeouts, stale edits, response failure and foreign ownership. These are field-model seams, not whole-network evidence. |
| C3 route startup | [Report](web-start-c3/report.json): actual startup function runs against controlled HTTPD/RTOS seams, including every registration failure and retained ownership when shutdown fails. |
| CYD routes and static workers | [Report](web-start-static-cyd/report.json): all 20 HTTP registrations, rollback, activation, both private-path boundaries, raw/gzip/playlist serving and four semantic controls. Methods and aliases are rejected before asynchronous admission or file open. The same frozen campaign also executes all 35 compact-page groups. |
| Compact CYD interface | [Report](web-page-cyd/report.json): 35 Node groups and eight semantic controls. First-row edits preserve the remaining rows, `keep` preserves private/legacy bytes, open networks require an explicit action, and stale time responses cannot overwrite a completed save. Existing OTA flows remain covered. |
| Existing C3 WebSocket publication | [Report](ws-status-c3/report.json): 22 actual status-loop scenarios, seven semantic controls and 57 JSON-parsed TEXT frames. Pending buffers, admission retries, playlist events and the real fragmented-message deadline work execute together. HTTPD/session/frame I/O and RTOS stepping are seams; prior TCP/TLS qualification is separate. |

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

SDK/Clang analysis, the complete new HTTP/TLS wire gates, explicit CSV-import
cutover and production image exports are recorded separately as they finish.
Host tests do not qualify physical RF recovery, NVS/SPIFFS power loss, device
clock accuracy, heap/stack high water, DMA behavior or browser layout.
