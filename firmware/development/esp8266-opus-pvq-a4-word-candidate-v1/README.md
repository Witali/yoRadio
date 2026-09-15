# Experimental Opus a4 word probes

CPU160/runtime QIO40, RAM-packet raw benchmark, audio output OFF.
Two3-byte CALL0 substitutions and25-byte leaf in old zero padding.
No new RAM/stack/table; all outside addresses unchanged; image903216 B.
SHA256:fe34751b8dae0cbd87a58a1b767aa02a82b006aa8b452f66065446dbc9dbdae9.

preflight.json contains actual linked/SAR/register/table proofs; host.json
contains24 exact PCM/state scenarios through510kbps and120ms. All30 A/B/A
completed: CPU19284.00988 /82.83819 /84.02250%, both high-bitrate gates PASS.
Accepted experimental raw baseline; not production or continuous-audio
qualification. No default change; ordinary radio restored OTA afterwards.
See docs/ESP8266_OPUS_ASM_PVQ_A4_WORD.md and CHANGELOG.md.
