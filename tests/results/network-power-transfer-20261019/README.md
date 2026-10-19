# Generation-qualified Wi-Fi audio power on CYD and C3

Production source: `bde1e645`. The shared policy and both audio integrations
implement N4 of the [network transfer design](../../../docs/CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md).
Existing task priorities, core affinities, audio backends and board wiring are
preserved. The C3 RSSI task now polls power intent every 100 ms while sampling
RSSI every two seconds; no additional C3 task is created.

| Gate | Evidence |
| --- | --- |
| Actual historical races | [Historical report](historical/report.json): sequential control passes; old EOF finish after a new accepted Play and old receive start after Stop each fail the intended safety assertion against exact `af8700e2e` bodies |
| Complete shared policy and actual C3 network task | [16 cases +4 controls](policy-c3-owner/report.json), strict warnings/ASan/UBSan; real C3 apply/poll/sleep bodies with pthread clock/RTOS and SDK seams |
| Actual audio control transactions | [Controls/receive](audio-controls-receive/report.json): C3 10 and CYD 9 groups; accept before queue, immediate EOF, late finish, Stop/late receive and queue failure |
| Actual CYD network receive | Same report: 9 groups for allocation/open/header/read errors, cancellation, EOF before PCM drain and old cleanup versus new Play |
| Actual permanent CYD network owner | [48 cases +6 controls](cyd-owner/report.json), including blocked SDK success/error followed by newer intent, retry budget, mode mapping and immutable active profiles |
| Three actual concurrent audio owners with real shared intent | [C3](maintenance-c3/report.json): 148 cases +13 controls; [CYD](maintenance-cyd/report.json): 83 +9, with HTTP/codec/output/RTOS seams |
| Existing C3 command and receive behavior | [2000 command operations](commands-c3/report.json), [37 receive/retry cases](receive-c3/report.json), [42 retained-TLS/adaptive-FLAC cases](receive-growth-c3/report.json) |
| Existing EOF and client/source checks | [Supplement](supplements/report.json): C3 EOF/PCM drain and 73 Node cases; named inputs frozen, source-shape checks are not behavioral concurrency proof |
| HTTP network status/admission | [16 cases +4 controls](http/report.json), parsed real maximum JSON including distinct desired/applied/error fields |
| WebSocket regression | [58 groups](websocket/report.json), maximum status JSON remains 4899 of 5120 bytes |
| Both real pinned GCC SDKs | [Component logs/configuration](sdk): ESP32 Xtensa v6.0.2 and ESP32-C3 RISC-V v6.1; application exports recorded separately |
| Full Clang AST | [CYD 50 units/81 warnings/0 errors](lint-cyd/report.json), [C3 65/127/0](lint-c3/report.json); no new warning instances/classes, all 649/758 pre-frozen inputs unchanged |
| N5 persistence precursor | [12 cases +7 controls](settings-precursor/report.json); no runtime/WebUI wiring yet |

Only serialized audio control establishes a generation. Receive/finish are
equality-qualified updates, so an old task cannot establish an old generation.
Only a permanent network task calls the SDK power setter; accepted Play does
not wait for that setter and remains independent of its errors. A driver call
runs outside the intent lock. A newer command can arrive during it, and the
next poll reconciles the latest desired mode. A stale error cannot consume the
new retry budget; a stale result after driver invalidation is discarded. Retries
are limited to three attempts per desired revision, 250 ms apart. `applied`
diagnostics represent the last successful SDK acknowledgement within that
driver lifetime; they do not prove instantaneous RF or electrical behavior.

ASan/UBSan campaigns preserve exact sources, generated units, commands and logs.
Each semantic control must fail its named assertion; unrelated sanitizer faults,
compiler failures and runner timeouts do not count. Host pthread critical
sections, SDK/netif/transport doubles and controlled clocks do not reproduce the
ESP32 scheduler or driver binary. No clean TSAN result, physical SMP proof,
energy saving, decode quality, RF latency or heap/stack margin is claimed.

The [warning delta](network-power-lint-triage.json) retains all diagnostics;
the new policy unit has zero warnings. [Code review](review/review.json) is
separate read-only evidence. [Qualification](qualification.json) records report
hashes and current input checks. Lint SDK/toolchain snapshots are stored under
short content-addressed `dependencies/` names; [archive-paths.json](archive-paths.json)
maps the original snapshot locations from unchanged manifests to those raw
files. [Manifest](manifest.json) binds every archived byte. No test executable,
live Wi-Fi credentials or private key is included.

N5 hostname/AP timeout integration, production exports and physical qualification
remain separate gates. The N5 source is committed as a standalone persistence
precursor and is not yet built into the application. The wider transfer plan,
including memory policy and architecture-specific decoder work, remains open.
