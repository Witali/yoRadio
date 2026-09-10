# Opus pulse-cache A/B — pure ROM, OFF

2026-09-10, source f20ed03. Diagnostic raw-decoder benchmark, CPU160/QIO40,
WordASM/ICDF/FIR ON, pulse-cache OFF. No audio TCP, normalization or PDM.
App 911760 bytes. Flashed via OTA; Wi-Fi/WebUI remain active during testing.

All 11 attempts retained. Attempt2 failed before decoding with allocation
error -9001 (DRAM16552 bytes). Memory later recovered without reset; this
does not prove a leak. All 10 completed attempts, including slow attempt1,
are preserved in order as run1..10. Do not report 11 successful tests.

See the candidate comparison and docs/ESP8266_OPUS_PULSE_WORD_BENCHMARK.md.
This is not a production firmware or evidence of continuous audio.
