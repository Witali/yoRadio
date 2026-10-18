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
| Concurrent CYD audio maintenance | [report](maintenance-cyd/report.json): PDM27, continuous DAC27 and legacy DAC26 scenarios with all three production owner loops and the actual adaptive FIFO; eight executable mutants detected by specific semantic assertions. |
| Existing CYD lifecycle | [report](maintenance-lifecycle/report.json): six vendor/Helix/minimp3 and adaptive/non-adaptive variants, including 2,000 concurrent Play/Stop commands per variant, stale callbacks, terminal drain and failure ownership. |
| Final backend pause and PCM regression | [pause](output-pause-final/report.json): PDM11/DAC17/legacy10 cases and two DMA ownership assertions; [gain](output-gain/report.json): 375 output and 5,801,300 arithmetic cases per backend. |
| Terminal transport preparation | [report](transport-prepare-close/report.json): 69 fault groups and five semantic mutants, including an incorrect socket shutdown before reserved reboot commit. Existing WebSocket shutdown behavior is preserved. |
| Fresh actual pinned TLS | [CYD](tls-cyd/report.json), [C3](tls-c3/report.json): eight verified TLS1.2 cases per SDK on the new transport source, using 117 vendor crypto units, trusted CA/SAN-verified independent OpenSSL clients, WANT/partial/peek/pending, backpressure and close alerts. |
| Complete CYD clang-tidy/static analysis | [report](lint-cyd/report.json): project31 units/39 warning instances, generated SDK overlay2/21, zero parse/tool errors. All33 source hashes were checked before preserving snapshots. |
| CYD cancellation publication | [report](maintenance-publication-cyd/report.json): final83 concurrent scenarios and nine specific semantic mutants. Maintenance is visible before a cancellation can make an output write fail; planned cancellation does not create a health fault. |
| Positive C3 HTTP adapter | [report](http-final/report.json): CYD243/C3246 groups and four semantic mutants per target, including activity/sleep admission and failure balancing. Acknowledged audio is an explicit seam here; owner qualification is separate. |
| Actual OTA HTTP/HTTPS pipeline | [report](wire/report.json): 44 localhost cases, 11 per board/transport, with actual generated SDK parser/URI/receive/response/session code and production OTA adapters. TLS uses real pinned ESP-TLS/crypto and independent CA/SAN-verified clients. |
| WSS transport regression | [report](wss-regression/report.json): 14 verified TLS cases and 14 real HTTPD/TLS session deletions per target on the updated transport. |
| Complete C3 clang-tidy/static analysis | [report](lint-c3/report.json): project54 units/100 warning instances, SDK overlay2/20, zero parse/tool errors. All56 unit snapshots match recorded hashes; final audio publication changes receive a separate focused pass. |
| Final C3 output and control regressions | [pause](output-pause-c3/report.json): staged12/direct10 and two exact ownership mutants; [boundaries](output-boundaries-c3/report.json): staged11/direct11 actual output-loop cases. [Commands](commands-c3/report.json) include 2,000 contended commands; [state](state-c3/report.json) includes 20,000 contended updates and locked metadata reset. |
| C3 unchanged playback and clock behavior | [PCM](output-gain-c3/report.json): four actual staged/direct writer variants each produce 12,331,776 identical bytes, plus648 normalizer cases. [EOF/RTC](eof-rtc-c3/report.json): ordered drain, delayed AAC PCM, stale/cancelled completion and the actual existing RTC wake-stub suite pass; no physical DMA or clock claim. |
| Concurrent C3 audio maintenance | [report](maintenance-c3/report.json): 148 scenarios across staged/direct and vendor/custom FLAC ownership branches, including native AAC and legacy arena leases. All13 specific semantic mutants are detected. All three production owner loops, adaptive FIFO, stream reader and resource-routing helpers execute; external codecs/allocator/output are explicit resource-tracking seams. |

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

Maintenance tests hold real production owners at external codec/HTTP/driver
and FIFO seams. They cover late encoded/PCM/control leases, blocked connect,
headers/read/close/cleanup, output writes/disable failures, finite lock budgets,
stale tokens, explicit Stop, queue failures, consecutive epochs and accepted
resume followed immediately by another maintenance. The empty-receive race
now requires the decoder's local generation to match before acknowledgement.
Timeout and late cleanup remain visibly distinct in snapshots. Stream metadata
and title clear while the station label, URL/codec and SmartStart intent persist.
The C3 matrix additionally covers pending retries, disabled watchdog, terminal
errors, an exited stream task after allocation failure, and the unchanged
actual idle-clock predicate. Maintenance is excluded from idle admission;
no additional sleep-service dependency was needed.

ASan/UBSan pass these matrices. ThreadSanitizer is **not qualified**: the first
idle case ran, but subsequent startup failed with its unexpected-memory-mapping
runtime error before the test's main marker. No runtime workaround was applied.

The terminal HTTP path prepares a bounded TLS alert and marks the transport;
it does not call synchronous lwIP socket shutdown before committing reboot.
HTTPD retains final descriptor deletion. Pinned lwIP's TCP close can wait for
FIN allocation even with a nonblocking descriptor; socket send timeout may
reduce that wait but does not turn the API into a nonblocking operation.

The complete OTA wire matrix preserves pending body bytes and a two-second
sender pause, rejects ten-second idle uploads with HTTP408, bounds unread-body
rejection, and commits reboot after response allocation failure. Real GET info
is the positive control for SDK request deletion; OTA POST must skip its purge
loop. The executable terminal-ESP_OK mutant entered actual SDK request deletion
and performed four body-purge receives, producing the expected controlled
semantic failure. Workspace and descriptor ownership remain separate and each
is released once. Audio acknowledgements, flash, image verification, RTOS and
field layouts are explicit seams in this network matrix.

CYD's complete lint run adds four OTA translation units. The 18 additional
warning instances comprise 16 repeats from the previously reviewed multipart
header and two `strcmp` explicit-comparison recommendations in the form adapter.
The two sites use the intended C nonzero/zero result; no new project memory
error was confirmed. Previous enum, branch-clone, bounded parser and generated
SDK diagnostics remain visible. A completed analysis is not a zero-warning claim.

The C3 lint increase is seven instances after consolidation: the new shared OTA
units add18, the thin donor upload wrapper retains8, and the former upload/HTTP
units contributed19. These are parser string/pointer recommendations; the count
does not represent19 repaired defects. The final changed CYD audio unit's
[focused analysis](audio-lint-publication-cyd/report.json) has one previous
header warning, zero errors and no new diagnostic signature. The final C3
[audio analysis](audio-lint-publication-c3/report.json) has four prior warning
instances, zero errors and no new diagnostic signature. Both focused reports
verify source stability during analysis.

Real TLS host builds retain the pinned SDK `esp_mbedtls_write` signedness
warning in its `written : ret` expression on the host ABI. The source is
unchanged; the positive/fatal/WANT tests are separate from this warning review.

Source snapshots and raw logs retain their recorded bytes and SHA256 values.
[archive-manifest.json](archive-manifest.json) inventories the campaign.
Newline conversion is disabled by the campaign's `.gitattributes` rule.
Executables, image fixtures, credentials and private data are not archived;
source generators and the documented software crypto inputs permit replay.

Remaining software gates: SDK application linking and all four
production application exports. Physical OTA, data preservation, interrupted
power and a separately established rollback bootloader remain pending.

Implementation contracts and code entry points are in
[the OTA design](../../../docs/CYD_OTA_TRANSFER_DESIGN.md).
