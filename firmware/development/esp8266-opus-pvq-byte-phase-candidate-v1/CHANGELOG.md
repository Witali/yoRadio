# Experimental byte-phase ASM candidate, 2026-09-17

Seven-instruction phase-specific flash-byte leaf instead of nine-instruction
SAR leaf, six existing a10 CALL0 sites. Exact symbolic result for all392
valid addresses/all32 word bits; no image-size/RAM/frame growth.

Parent: accepted exp2-table32,79.626521% raw CPU192. All30 physical
A/B/A attempts completed with exact PCM:192 CPU79.618646 /80.282333 /
79.643604%;128 CPU71.839771 /72.508813 /71.860083%. Candidate REJECTED:
both high-bitrate speed gates fail. Fourteen final regressions pass/0skip
in95.26s, including the linked proof chain and independent evidence checks.
No production default or C fallback change; application-only image.
Prior diagnostic C-radio restored via OTA, HTTP200 in107.34ms, WS/index,
station167, volume100, balance0 and unchanged playlist verified. It is
stopped as before; this is not a new production or live-I2S qualification.

See [full description](../../../docs/ESP8266_OPUS_ASM_PVQ_BYTE_PHASE.md)
from the repository docs directory (the canonical document is
`docs/ESP8266_OPUS_ASM_PVQ_BYTE_PHASE.md`).
