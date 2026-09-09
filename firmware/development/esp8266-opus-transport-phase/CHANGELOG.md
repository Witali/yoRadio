# Opus transport-phase diagnostic — 2026-09-09

Source8534cd7, application882304 bytes. Same PDM32 IRAM/word-ASM stream-only
profile as the previous experiment. ICDF word and PDM32 batch OFF; no raw
benchmark/runtime stats/SPIFFS log. Config/hash details in manifest.

TCP connect is now nonblocking with a10-second shared address-attempt
deadline, SO_ERROR verification,50-ms cancellation checkpoints. DNS remains
a separate blocking SDK stage. Diagnostics add16 DRAM bytes only in this
profile; HTTP health reuses existing1088-byte scratch instead of384-byte
stack body. A health snapshot now reports phase plus latched terminal
refill result, errno and compressed bytes remaining.

OTA app0→app1 passed. Both25-second SILK12 local and real Intense56 tests
FAILED continuity, with all failed HTTP observations retained. The new
fields identify the original stop: STREAM_FILL_TIMEOUT=4, errno116,
input_bytes=0, followed by phase2 (TCP connect). This is not a prolonged
Opus decode or an assumed20-second close. Warm reconnect sometimes returns
to real PCM; the real station later still hit decoder initialization failure.

Local SILK at least temporarily keeps PCM close to realtime, but short DMA
underruns remain. Server log spacing suggests one40-second connection after
frequent HTTP polling ended; that is not proof of continuous PCM and needs
a sparse-poll repetition. No network/CPU samples were filtered to claim pass.

Next: isolate HTTP/TCP memory pressure, compare pure ICDF decode A/B, and
test PDM32 span filling separately. This binary is diagnostic, not production.
