# tell-inline + update-fast ASM benchmark

Built from b4f96f0c on 2026-09-13. This is a raw-codec diagnostic image,
not a production release and not a claim of successful live I2S playback.

- Four exact tell_frac inline sites and two no-normalize update fast paths.
- CPU160 / QIO40 / 16-KiB cache; original C/GCC snapshot untouched.
- Same packets preloaded into RAM, no audio network/demux/PDM during timing.
- ASAN/UBSAN host PCM/PLC/reset/OOM/guards passed; 41 Node regressions passed.
- App 903328 bytes: +112 versus best tell-inline. Static RAM unchanged.
- OTA app-only; no partition, SPIFFS, NVS or UART operations.

Physical A/B/A completed: 10 tell-inline, 10 combined, 10 repeated tell-inline.
192k CPU medians 88.125 / 92.959 / 88.142 percent. Combination is slower at
all five bitrates; rejected, default unchanged. Exact PCM in all 30 runs.
Min sampled DRAM 2272 / 904 / 2616 B; no decoder errors, stack free 1660 B.
Ordinary live512-idle3s firmware restored by OTA; HTTP smoke passed.
Full evidence: comparison.json and docs/ESP8266_OPUS_ASM_TELL_UPDATE.md.
Not a live-audio qualification and not achievement of the 70% CPU goal.
