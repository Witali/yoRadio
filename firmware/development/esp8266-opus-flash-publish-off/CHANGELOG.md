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

## Completed control series (2026-09-11)

All ten attempts completed with matching PCM hashes, packet counts and sample
counts. All raw reports/logs are retained. A completed measurement does not
mean continuous output: nine SILK12 windows passed, and every24/64/128/192
window failed the digital continuity gate. The completed ON comparison is
saved in ../esp8266-opus-flash-publish-on/comparison.json.

| Corpus | Median pipeline CPU budget | Continuous windows | Median / maximum DMA misses | Lowest observed free DRAM |
|---|---:|---:|---:|---:|
| SILK mono12 | 36.862% | 9/10 | 0 / 1 | 7152B |
| Hybrid mono24 | 68.338% | 0/10 | 40 / 47 | 3244B |
| CELT stereo64 → mono | 79.208% | 0/10 | 49 / 53 | 1732B |
| CELT stereo128 → mono | 89.733% | 0/10 | 168.5 / 2337 | 364B |
| CELT stereo192 → mono | 99.145% | 0/10 | 1023.5 / 2243 | 500B |

The pipeline includes hashing, normalization/PDM and charged interrupts;
these percentages are not raw decoder CPU. Maximum measured decode wall
calls were8071/63888/69028/81092/87435us. They can include preemption and
cache effects; these are not proven worst-case computation times.

Attempt1 had a status timeout and attempt8 an ECONNRESET observation. Both
were observed to completion without replacing/restarting them. The lifetime
minimum heap changed from23708B before attempt1 to192B afterwards and stayed
there; it is not a fresh192B low-water event on every later attempt. This
fails the memory reserve gate; it neither proves a leak nor leak freedom.

The final FIFO-empty latch was zero despite the DMA misses: the neutral-word
fallback kept hardware fed, not necessarily audio. No analog capture was made.
The corpus and all ten results are checked by
`tests/esp8266-opus-flash-publication-evidence.test.js`.
