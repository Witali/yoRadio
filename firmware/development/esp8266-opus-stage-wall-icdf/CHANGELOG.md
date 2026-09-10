# Opus live ICDF-word comparison, 2026-09-10

Source3980fb0, 884864-byte experimental OTA image. Same pipeline as stage-wall,
with ICDF flash-word reads ON. No added RAM/IRAM; exact PCM evidence is already
saved in the decoder regression corpus. OTA to0x10000 succeeded.
SILK has a modest timing difference but still misses DMA deadlines. CELT runs
include startup reserve failure, HTTP timeouts and reconnects: no full-path
speed qualification. Production defaults remain unchanged.

[Method, results and limits](../../../docs/ESP8266_OPUS_LIVE_STAGE_PROFILE.md).
Raw reports, including failed requests, are in results/.
