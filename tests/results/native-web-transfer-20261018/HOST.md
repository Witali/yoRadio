# Native WebUI transfer: source and host qualification

2026-10-18. Work in progress. This checkpoint records software evidence; it
does not certify full RFC conformance, physical flash durability, ESP32 task
timing, heap admission or audio continuity. New production firmware images are
still pending. Earlier images remain in their original development folders.

| Scope | Frozen result |
| --- | --- |
| Portable WebSocket message/control core | [report](message/report.json): all 1,112,064 Unicode scalars, 5,494,656 scalar fragment assemblies, 296,608 independent UTF-8 oracle inputs, 65,536 Close codes, capacity/time/control checks; four semantic mutants detected. |
| C3/CYD radio publication | [report](radio/report.json): actual shared controller and per-target state, real host locks/files, candidate index prepared before publishing CSV/index under the radio lock; existing concurrent command tests retained. |
| Real index I/O | [C3](index-c3/report.json), [CYD](index-cyd/report.json): exact offsets, corrupt/stale caches, missing CSV, bounded rows and injected write/flush/close/rename failures. |
| Multipart headers/streaming | [report](multipart/report.json): 896 header/body checks, actual C3 receiver and four historical negatives; [previous multipart/form/sink suites](multipart-existing/results.json) pass. |
| Full upload handlers | [report](uploads/report.json): CYD 69, C3 68 scenarios; 10 actual CYD reboot scenarios; 105 actual file-pair transaction scenarios. Namespace aliases are rejected before publication; raw cleanup holds the storage mutex. |
| Actual Wi-Fi persistence | [CYD](wifi-cyd/report.json): 44 groups; [C3](wifi-c3/report.json): 41 scenarios plus two historical negatives. C3 interior-CR acceptance and destructive post-commit re-read are fixed. |
| Earlier file/network warning regressions | [report](web-regressions/report.json): previous bounds, retained backups, serialized readers, EOF/error and small-name controls pass. |
| CYD static/startup/UI | [report](static-startup-cyd/report.json): actual static/start functions with explicit HTTPD/RTOS seams; all route failures, stop/release failure ownership, recovery pages; 15 executed JS tests using actual Node FormData/Request. No visual browser qualification. |
| C3 startup | [report](startup-c3/report.json): actual startup/abort functions; failures before the listener roll back; failures after a live listener retain ownership and reject duplicate starts. C3 producer has no stop API. |
| Generated SDK HTTPD | [CYD](httpd-cyd/report.json), [C3](httpd-c3/report.json): each 623 function checks, 624 emulated size-cap checks and 14,332 receive-split checks through the actual SDK HTTP parser/read/pending pipeline. Historical malformed offers/folding/empty Content-Length/session-reuse failures detected. |
| CYD WS adapter | [final report](ws-cyd-final/report.json): 57 groups; actual service functions and explicit transport/frame seams. Fragmented commands, split UTF-8, Ping/Close, message limits/deadline, fd reuse and ordinary GET rejection pass. The earlier 56-group snapshot remains in `ws-cyd/`. |
| C3 WS adapter | [report](ws-c3-final/report.json): 5189 cases and four historical negatives; actual service functions, pinned SDK framing, short I/O/WANT/deadlines, fragments/control, JSON sanitizer and ordinary GET rejection. Host layout is not a target RAM result. |
| TLS transport ownership/failures | [report](transport-faults/report.json): 65 groups and four semantic mutants; actual production transport with explicit NVS/TLS/crypto seams. Cryptographic acceptance is a separate real-backend gate. |
| Actual pinned TLS | [CYD](tls-cyd/report.json), [C3](tls-c3/report.json): eight cases each, 117 real vendor crypto units under ASan/UBSan, MbedTLS 4.1.0/4.1.1, independent OpenSSL client verifies CA/SAN. Peek/pending, backpressure/partial writes, WANT directions, Close alerts, fatal EOF and handshake deadline pass; wrong CA/name/TLS1.3 reject. |
| Private provisioning format | [report](tls-bundle-profile/report.json): six structure/output/container checks. Qualified unencrypted RSA PKCS#1 succeeds in real TLS; valid matching PKCS#8 is rejected because the pinned private/public pair checker rejects that parser path. Embedded verification stays strict; rejected profiles do not change NVS. |
| Actual HTTPD/application TCP chain | [report](tcp-integrated/report.json): 164 cases and 168 real SDK session deletions per target; three original-SDK negatives per target. Parser, pending/unrecv, URI/pre/post hooks, command assembly, control/Close and real descriptor reuse run together. Ordinary GET `/ws` now returns HTTP400 before WS allocation. |
| Combined actual HTTPD/application/TLS chain | [report](wss-integrated/report.json): 14 trusted localhost TLS1.2 cases and 14 actual HTTPD/TLS session deletions per target. Actual production transport, pinned ESP-TLS/crypto, PSA SHA-1/Base64 Accept, SDK parser/session/framing and handlers run together. Independent OpenSSL verifies CA/SAN; fragments/control/Close and omitted/wrong Upgrade cases pass. |

The C3 upload leg deliberately uses actual CYD Wi-Fi persistence as its Wi-Fi
API seam; the separate `wifi-c3` suite executes the actual C3 functions. The
upload index-preparation seam is complemented by the actual radio/index suites.
File-pair rollback is not crash atomic: interrupted mixed generations require
boot catalog validation/rebuilding. Multi-asset batches may partially commit.

Source snapshots and raw logs are preserved with hashes. `archive-manifest.json`
records copied files; `.gitattributes` disables newline conversion in this
campaign. Header field models, SHA sample seams and emulated size caps do not
replace target ABI checks or a full live server. Actual TLS tests use ephemeral
Linux temporary identities and archive no certificates, private keys, bundles
or NVS images. Their software crypto/type/NVS seams are recorded in each report.

## Compiler and lint checkpoint

Both pinned SDKs compile main, native TLS transport and generated HTTPD
components with Clang. The C3 build needed local wrappers for the shared
message/JSON headers. The FLAC GCC optimization pragma is now GCC-only; GCC
behavior is unchanged. [Final component evidence](sdk-components/report.json)
includes commands, generated-overlay manifests and configuration. These are
component builds, not new firmware hand-offs.

| clang-tidy scope | Own units/warnings | Generated SDK units/warnings | Errors |
| --- | --- | --- | --- |
| [CYD](lint-cyd/report.json) | 27 / 21 | 2 / 21 | 0 |
| [C3](lint-c3/report.json) | 51 / 93 | 2 / 20 | 0 |

The earlier own-code baselines were CYD 24/8 and C3 50/77. The expanded run
adds the TLS unit, CYD upload/reboot units and shared inline parsers; generated
SDK diagnostics are reported separately. New parser/transport warnings concern
explicit string comparisons and pointer increments in sequenced conditions.
No new own-code memory error was confirmed by this pass.

SDK `strcpy`/`strcat` warnings use a validated 24-byte key, constant UUID and a
larger fixed output array. The two cleanup null warnings follow the overlay's
defensive `sd && ...` branch; actual session processing calls delete only after
successful request creation with a session. The integrated lifecycle test checks
that invariant on the exercised paths; this is not presented as a repaired null
dereference.

Focused checks after the HTTP400 fix preserve the full reports:
[C3](ws-lint-c3/report.json) has three previous project warnings and zero errors;
[CYD](ws-lint-cyd/report.json) has zero project warnings/errors. Both have zero
new diagnostics. SDK component builds were repeated for the changed sources.

The existing C3 AAC owner-view warning remains deferred as previously recorded
in [the warning campaign](../native-warning-fixes-20261018/deferred/README.md).
Its proposed patch is not applied or claimed as qualified here.

## Remaining gates

- Final production GCC images/maps/configuration comparison for CYD PDM,
  continuous DAC, legacy DAC and C3; archive every successful hand-off image.
- Physical internal/DMA heap, HTTPD/audio stack high water, reconnect/churn,
  slow clients and audio continuity. Preserve CYD stream core0/priority3,
  decode core1/priority5 and output core1/priority6, and its existing hardware.
