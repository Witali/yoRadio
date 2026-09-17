# Immediate refill plus leased PCM queue — 2026-09-17

Ordinary diagnostic radio, all18 accepted ASM stages, TCP536/window2440,
RX14, I2S PDM32 GPIO3, DMA2x128, PCM2x960 mono, consumer stack1536,
main audio stack5120, Opus input1024/scratch6144 and reserve4096.

The explicit FULL/YIELD immediate-refill correction is included. No PCM
arithmetic change. App890240B, SHA256 in manifest; OTA succeeded.

DLF24 live series: **0/10 qualified**. Six incomplete timing windows;
four complete windows had no PCM progression. Returned init diagnostics
include scratch fragmentation (stage8) and reserve rejection (stage10).
Lifetime heap minimum2936B. One unsupported-stream status came from the
format-detection path, not proof of an unsupported Opus frame duration.
Stopped neutral-DMA counts are not active-audio loss measurements.

Two local saved-capture windows were incomplete. An extra live observation
with a deliberately extended15s diagnostic HTTP timeout returned22.027s
PCM in34.231s board time,8046 underruns: also FAIL, not a WebUI latency pass.
Output-worker error stayed0 in returned samples, stack watermark1160B.
No claim of acoustic quality or normal continuous playback.

Host tests: exact18-stage loaded-image tests pass. Runtime/input/DMA tests
passed11/13 initially; two CMake selector tests could not launch CMake
(ENOENT). With the installed CMake explicitly selected, all3 selector tests
passed. Both the initial failure and corrected run are archived, not hidden.
This queue profile remains experimental; production defaults unchanged.
