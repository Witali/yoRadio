# Experimental byte-phase ASM candidate, 2026-09-17

Seven-instruction phase-specific flash-byte leaf instead of nine-instruction
SAR leaf, six existing a10 CALL0 sites. Exact symbolic result for all392
valid addresses/all32 word bits; no image-size/RAM/frame growth.

Parent: accepted exp2-table32,79.626521% raw CPU192. This candidate has
NOT been timed or qualified on the board. Three local regressions pass;
parent PCM golden evidence is inherited, not relabeled as a new target run.
No production default or C fallback change; application-only image.

See [full description](../../../docs/ESP8266_OPUS_ASM_PVQ_BYTE_PHASE.md)
from the repository docs directory (the canonical document is
`docs/ESP8266_OPUS_ASM_PVQ_BYTE_PHASE.md`).
