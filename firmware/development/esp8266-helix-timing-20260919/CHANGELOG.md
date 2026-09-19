# MP3/AAC decode-only timing — 2026-09-19

Diagnostic image, not a production release. CPU160/QIO40, Helix MP3 SSO mono,
Helix AAC-LC 512-sample blocks. Existing WebUI/OTA remain available.
`POST /api/native/opus-benchmark` starts the alternative Helix matrix;
GET explicitly reports `helix_timing=true` so tools cannot label it Opus.

Six own 48-kHz stereo clips: MP3 64/128/320 and AAC-LC 48/128/320 kbit/s.
Twenty consecutive compressed frames per clip, one warm-up and ten scored
rounds, fresh decoder state between rounds. All output discarded after decode.
Compressed frames are copied to RAM before each measured call. Task runtime
excludes other tasks; wall time and measurement overhead are recorded separately.

Source, generator, lifecycle tests and procedure:
`docs/ESP8266_CODEC_TIMING_BENCHMARK.md`.
`manifest.json` authenticates app/config/source/fixture metadata.
Restore `firmware/development/esp8266-main/app.bin` after measurement.
