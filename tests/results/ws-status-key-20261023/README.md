# Portable WebSocket status comparison, 2026-10-23

CYD and C3 now compare each status-key field and logical NUL-terminated string.
Structure padding and bytes after a string terminator no longer trigger redundant
status revisions/publications. Type layouts, capture, heartbeat, work admission,
queue ownership, task affinity and production hardware settings are unchanged.
This is a portability correction (P3), not a reproduced production crash.

| Check | Actual result |
| --- | --- |
| Old CYD/C3 with padding-only changes | Both fail the exact publication assertion |
| Current CYD host | 59 fixture groups, ASan/UBSan; all 18 scalar/4 string changes detected |
| Current C3 host | All 42 status-loop cases + 7 semantic controls, ASan/UBSan |
| Target GCC | Separate ESP32 Xtensa and ESP32-C3 RISC-V objects, zero diagnostics |
| Focused clang-tidy | CYD 1 / C3 2 existing warnings, zero errors or new warnings |

The new tests modify only padding selected by offsetof/member-size masks, then
check real status publication before heartbeat. Every scalar and visible string
is tested separately; logical string tails are tested too. CYD final before/after
use byte-identical harness/runner bytes. C3 full-suite mode retains all earlier
22 cases and seven controls; filtered before mode is explicitly not a full suite.

Both suspicious-memory-comparison warnings disappeared. The remaining diagnostics
are the existing bounded CYD RSSI conversion, C3 command aliases and a diagnostic
dead store. The HTTPD NULL-session trace requires a caller state excluded by the
SDK success/error flow; negative timezone promotion is intentionally signed.
Neither was changed just to reduce the warning count.

target-4 is the final focused target qualification. Its eight actual commands
use existing SDK compilation databases without configuring/building a full app.
It captures each dependency union and verifies captured source/header/config/
database/compiler inputs before/after analysis. Actual response/specs and analyzer
identities are frozen before the dependency walk, then rechecked. CYD remains
SDK6.0.2/240 MHz/SMP; C3 SDK6.1/160 MHz/unicore. The two genuine ELF32 relocatable
headers/machine identities and object hashes are retained; object bodies are omitted.
No linked firmware or physical timing/resource/acoustic result is claimed.

Target attempts 1 and 2 retain their actual preflight failures. Attempt 3 actually
compiled/analyzed both units but lacked complete captured compiler context; it
remains limited history. Attempt 4 includes that context after independent review.
The initial CYD before-run preceded the final added string-tail regression and is
also history; the final before-run matches the successful harness exactly.

Reports, logs, generated host text, frozen project source/header copies and exact
validation scripts are retained. External SDK/toolchain headers and executable
bodies remain recorded hashes, not replayable payloads. The archive verifies its
own bytes, not fresh compilation, full-app qualification or a new sanitizer run.
Reproduce host behavior with tests/run-cyd-websocket.py and
tests/run-c3-websocket-status.py --output FRESH_DIRECTORY from the repository.
The latter's default runs the complete suite.

No physical device, serial/reset/flashing or production firmware export occurred.
Production CYD stream core0 and decode/output core1 remain unchanged. Deferred
codec work is untouched; this correction is an independent WebSocket change.
