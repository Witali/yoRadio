# Opus flash-output publication control

2026-09-11, source eee18c2, app903664B. Diagnostic only, not a release.
Own tone/noise packets from flash,12/24/64/128/192kbps; no audio TCP, Ogg or
ICY. Wi-Fi/WebUI remain enabled. The full pipeline includes PCM hashing,
gain/normalization, PDM32 and GPIO3 DMA; its task CPU is NOT decoder-only CPU.
CPU160/QIO40, two512-word buffers, publication OFF, FIR/ICDF/word helpers ON.

Matched ON image differs only in publication; same benchmark source and
fixture header hashes are recorded in both manifests. Each case has one
warmup and100 measured rounds of12 packets (24s PCM), decoder reset each
round, uninterrupted DMA across measured rounds. This is repeated short
audio, not24s of distinct decoder history. Ten attempts are planned;
attemptN.json/log preserve all results including failures. No speed or
continuity improvement is claimed before comparing all attempted runs.

Runner:
`tools/esp8266_opus_profile/run_output_series.ps1 -Directory firmware/development/esp8266-opus-flash-publish-off -Fixtures .build/esp8266-opus-board-through192 -Attempts 10 -IntervalMs 30000`

Use app-only OTA. Do not restart an unknown/running benchmark on an
observation timeout. See docs/ESP8266_OPUS_PCM_PUBLICATION.md for context.
