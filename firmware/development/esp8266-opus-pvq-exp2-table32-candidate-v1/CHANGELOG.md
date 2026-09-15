# Experimental direct exp2 table32 — 2026-09-15

Native ESP8266 Opus ASM raw benchmark; not production or speed-qualified.
Independent parent: accepted pvq-index-half80.019979% CPU192, CPU160/QIO40.
Replace one L16SI by L32I, change index scaling and the sole-reader literal.
Eight signed32 constants reuse32 bytes of proven dead encoder flash code.
No extra helper, call, instruction count, RAM, stack or image-size growth.
App903216bytes;24 exact PCM cases and134976 linked numeric cases passed.
No target upload: board unavailable. Physical A/B/A and live I2S/WebUI pending.
Six focused tests and the full184-test related suite PASS/0skip.
Final-tests.log and three failed board-status observations are retained.
The mandatory hardware stage is blocked until the board is reachable again;
no serial/reset fallback or network-adapter change was performed.

SHA256:7209b07ddde4febf7078e90100bfac3b3e4d9a7538e1ce44beaac95c30738649.
See docs/ESP8266_OPUS_ASM_PVQ_EXP2_TABLE32.md; preserve all proof/manifest/log files.
