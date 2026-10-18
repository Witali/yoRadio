# Native OTA transfer qualification

2026-10-18. Software checkpoint; implementation and integration are in progress.
No board has been flashed or reset during this campaign. Physical flash,
DMA quietness, timing, power loss, heap and stack admission remain separate.

| Scope | Frozen evidence |
| --- | --- |
| Shared image sink, CYD IDF6.0.2 | [report](sink-cyd/report.json): 1,529 fault groups under ASan/UBSan; five executable mutants detected. Actual sink and pinned image layouts; flash and verifier failure seams. |
| Shared image sink, pinned C3 IDF6.1 | [report](sink-c3/report.json): the same 1,529 groups and five mutants against the donor SDK layouts. |
| Actual image verification, CYD | [report](image-cyd/report.json): 11,396 scenarios with 15 verbatim SDK functions and actual PSA SHA implementation; checksum, SHA and exact-length mutants detected. |
| Actual image verification, C3 | [report](image-c3/report.json): 11,396 scenarios against the pinned donor verifier and software crypto. |
| Reboot reservation | [report](reboot/report.json): 208 scenarios per target, including 200 real thread admission/request races, deferred requests, stale/duplicate tokens and allocation-free commit. |
| Existing upload/reboot behavior | [report](reboot-regressions/report.json): CYD69/C368 upload scenarios, CYD10 reboot cases and 105 file-pair transaction scenarios. |
| Initial CYD backend pause | [report](output-pause-initial/report.json): PDM10, continuous DAC16 and legacy DAC9 cases; two ownership mutants detected. This snapshot precedes the subsequent cancellation and three-owner maintenance implementation. |
| Shared form/HTTP and target adapters, initial | [report](http-initial/report.json): CYD243/C3183 groups, four/one executable mutants detected. Actual pinned SDK buffered receive, response send, context and request-cleanup functions. This C3 checkpoint deliberately rejects positive OTA until acknowledged audio maintenance is integrated. |
| Multipart compatibility | [report](multipart-current/report.json): 896 header checks, five actual receiver variants, four historical receiver negatives and the current C3 OTA runner. |
| CYD routes, startup and UI | [report](static-startup-cyd/report.json): actual static/startup functions under ASan/UBSan, every route failure and retained ownership after stop failure; all22 Node tests pass, including native ordered FormData/XHR and recovery behavior. |

Image tests cover incomplete and damaged images, wrong chip/project, exact
application caps, spare-slot validation, read/map faults, trailing bytes and
an old flash tail. In the latter case the SDK end check can accept the old
tail; the additional exact uploaded-length check rejects it. Fixture image
generation has an independent Python checksum/SHA oracle. Production unsigned
ESP32/C3 profiles are the qualified scope; signed-image profiles are excluded.

Host flash, RTOS, HTTP, driver and layout seams are stated in each report.
Actual software crypto does not establish device flash or DMA behavior.
The initial HTTP matrix covers a two-second upload pause beyond the default
one-second SDK timeout, buffered pending bytes, both WANT directions, the
ten-second idle and 180-second absolute budgets, a 20-second synchronous
maintenance operation, late acknowledgement without erase, metadata with no
running partition, foreign session ownership, and response OOM/zero-send
after activation. HTTP field models and fake transport readiness are explicit
seams; real TCP/TLS and the complete parser lifecycle are separate gates.

The reboot tests preserve C3 first-request timing and CYD earliest-request
timing while preventing an already reserved OTA transaction from losing its
reboot service. A failed response after activation must still commit reboot.

Source snapshots and raw logs retain their recorded bytes and SHA256 values.
[archive-manifest.json](archive-manifest.json) inventories the campaign.
Newline conversion is disabled by the campaign's `.gitattributes` rule.
Executables, image fixtures, credentials and private data are not archived;
source generators and the documented software crypto inputs permit replay.

Remaining software gates: three concurrent audio owners and late cleanup,
C3 maintenance integration, actual HTTPD/form/transport lifecycle over HTTP
and verified TLS, final SDK compilation, lint, and all four
production application exports. Physical OTA, data preservation, interrupted
power and a separately established rollback bootloader remain pending.

Implementation contracts and code entry points are in
[the OTA design](../../../docs/CYD_OTA_TRANSFER_DESIGN.md).
