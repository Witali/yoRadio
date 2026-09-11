# CELT LX106 rotation: matched raw candidate

2026-09-11, source05eff07, app902544B. Diagnostic only, not a release.
All settings and fixtures match ../esp8266-opus-rotation192-off except
OpusRotationLx106=ON. No PCM quality, buffer size, CPU/flash rate or codec
coverage changes. Static DRAM/IRAM and the DMA ISR are unchanged; flash
text is384B smaller. See the control changelog for complete methodology.

The existing152B assembly function uses a16B local stack frame, no calls
or IRQ masking, and no new IRAM allocation. That does not establish the
whole decoder's stack use, speed or live-radio continuity.

Host checks passed; actual target execution, golden PCM and timing remain
pending. Do not promote this profile based on compilation or a host model.

```powershell
tools/esp8266_opus_profile/run_raw_series.ps1 -Directory firmware/development/esp8266-opus-rotation192-on -Fixtures .build/esp8266-opus-board-through192 -Attempts 10
node tools/esp8266_opus_profile/compare_raw.cjs --reference firmware/development/esp8266-opus-rotation192-off --candidate firmware/development/esp8266-opus-rotation192-on --switch opus_rotation_lx106 --runs 10 --output firmware/development/esp8266-opus-rotation192-on/comparison.json
```

Use application-only OTA, not UART. Keep all failed/slow attempts. A speed
improvement alone does not meet the goal of uninterrupted Opus radio.
