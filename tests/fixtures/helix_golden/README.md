# Helix decoder golden fixtures

These short, deterministic MP3 and ADTS AAC streams exercise the complete
yoRadio Helix decode path. `tests/esp8266-helix-golden.test.js` decodes every
fixture twice: once through the retained 64-bit reference arithmetic and once
through the ESP8266 LX106 fixed-point implementation. The resulting PCM byte
streams must have identical lengths and SHA-256 hashes.

The clips are intentionally small so the regression test remains practical in
local and CI builds. They contain stereo 44.1-kHz audio at 320 kbit/s, cut with
FFmpeg using stream copy from the deterministic codec benchmark fixtures.
