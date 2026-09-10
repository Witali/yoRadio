# Opus pulse-cache A/B — pure ROM, ON

2026-09-10, source f20ed03. Same settings as pure OFF, only pulse-cache ON.
App 912480 bytes (+720 flash). OTA and 10 completed raw benchmarks retained.
Every PCM hash matched. No static RAM or stack increase in target tests.

Median decoder task budget: SILK12 24.533%, Hybrid24 56.986%, CELT64 79.082%,
CELT128 100.847%, CELT510 195.720%. CELT64 is 6.61% slower than OFF.
Rejected for normal radio; source experiment is recoverable from f20ed03.

All observations retained, including timeouts in runs8/10. CPU comparison
is valid for completed attempts, but passed=false records OFF's failed
allocation attempt. Run6 SILK task exceeds decode-wall by344us over120
packets: task timing includes snapshot/yield overhead outside decode-wall.
Neither value is clamped or silently discarded.

Host PCM/phase/unit/Xtensa reports are archived alongside this firmware.
No physical PDM/live qualification was attempted with this slower variant.
