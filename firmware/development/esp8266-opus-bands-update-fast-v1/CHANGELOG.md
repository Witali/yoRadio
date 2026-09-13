# Experimental Opus ASM update-fast — 2026-09-13

- Source 374d136a, CPU160, profile QIO40/cache16, raw RAM-packet benchmark.
- Two no-normalize ec_dec_update fast paths; original GCC normalization fallback.
- App 903120 B, +128 flash; unchanged static RAM and 5120-B audio stack.
- 10 control + 10 candidate + 10 repeated control, five bitrates each.
- Exact PCM/PLC/reset/OOM, 100000 ASM-model and 100000 C state tests,
  17 regression tests. All physical attempts retained, no observation errors.
- CPU192 median 91.878%, control 92.911% / repeated 92.844%.
- NOT accepted: ~1.1% high-bitrate gain is below ~1.9% mono12 regression.
- Best prior tell-inline remains 88.136%; target70% NOT reached.
- Ordinary I2S PDM radio restored via OTA; this is not a live-qualified release.
- See docs/ESP8266_OPUS_ASM_UPDATE_FAST.md, comparison.json and link-relaxation.json.
