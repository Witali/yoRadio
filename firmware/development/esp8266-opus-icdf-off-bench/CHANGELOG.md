# Physical ICDF A/B baseline — 2026-09-09

Source8534cd7,909120-byte diagnostic app. CPU160/QIO40, Opus word ASM ON,
ICDF flash-word OFF, PDM32 IRAM ON/batch OFF, SPIFFS cache OFF, short Web
priority policy. Raw benchmark/runtime stats ON; Opus input1024/scratch6144.
No saved settings, playlist or SPIFFS changed by application OTA app1→app0.

Two complete physical runs passed all five PCM fingerprints. Packets are
copied from embedded own fixtures to RAM before timing. Decode timing
excludes network audio, Ogg, normalization and PDM output. Task time still
includes charged ISR/instrumentation. Each mode:120 packets/2.4 seconds PCM.

Mean CPU budget: SILK12 59.183%, Hybrid24 93.085%, CELT64 75.993%,
CELT128 94.317%, CELT510 152.575%. Paired ON results and interpretation are
in ../esp8266-opus-icdf-on-bench/comparison-results.json and CHANGELOG.md.
This binary is not evidence of continuous radio playback.
