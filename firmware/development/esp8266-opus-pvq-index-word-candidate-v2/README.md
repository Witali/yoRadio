# Signed PVQ index word-load candidate v2

Experimental raw Opus ASM benchmark, not ordinary radio or a default profile.
CPU160MHz/runtime QIO40, packets in RAM, physical audio output OFF.
Native application-only OTA; no UART commands or reset on GPIO3.

Three patches,total35 bytes. Early original return store,29-byte fixed-J
helper, exact signed16 extraction by SLLI16/SRAI16. No added RAM/frame/table.
Image903216 B. Host24 cases and137792 linked prefix cases exact.
Physical speed pending; parent endpoint-word80.99456% CPU192.

v1 was rejected by the assembler (SEXT unavailable); never flashed.
v2 uses the supported exact shift pair. Failure log is retained.
See docs/ESP8266_OPUS_ASM_PVQ_INDEX_WORD.md and preflight.json.
