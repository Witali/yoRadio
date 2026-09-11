# Opus stride1 v2: register-carry ASM candidate

2026-09-11, source3aeac48, app902704B. Same settings/corpus as matched control
../esp8266-opus-stride1-off except OpusRotationLx106. Experimental, default OFF.
Only stride1 uses a specialized leaf; all other strides remain original C.
Fifteen instructions per iteration, one load, no local stack, same rounding
and int16 wrapping. No new buffer or IRAM, no IRQ masking, no quality change.

Host C ASan/UBSan1512 vectors; actual assembly-text model1120 stride1 vectors
(511264 coefficients), exact with guards/ABI checked. Full host block-output
PCM corpus rerun:11 cases exact, including mixed SILK/Hybrid/CELT. These are
not physical ASM timings. Static RAM and ISR unchanged; flash text is216B
smaller than control. Build/manifest checks pass; board10+10 raw and then
flash-to-PDM/live-radio qualification still pending. Do not promote yet.

```powershell
tools/esp8266_opus_profile/run_raw_series.ps1 -Directory firmware/development/esp8266-opus-stride1-on -Fixtures .build/esp8266-opus-board-through192 -Attempts 10
node tools/esp8266_opus_profile/compare_raw.cjs --reference firmware/development/esp8266-opus-stride1-off --candidate firmware/development/esp8266-opus-stride1-on --switch opus_rotation_lx106 --runs 10 --output firmware/development/esp8266-opus-stride1-on/comparison.json
```
