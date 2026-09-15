# Experimental exp2_table8 word-load candidate — 2026-09-15

Native ESP8266 Opus ASM raw benchmark, not production or speed-qualified.
Parent: accepted pvq-index-half80.019979% CPU192, not the pending logN candidate.
CPU160/QIO40 unchanged. Replace one emulated signed16 flash read with
phase-specific aligned32 ASM; no scratch register, stack slot or extra table.
App903216bytes, static RAM/IRAM and stack unchanged.24 host cases exact,
131584 linked numeric cases verified. No target upload: board unavailable.
Four focused regressions and the full178-test related suite PASS/0skip.
The complete final-tests.log and three failed board observations are retained;
no serial recovery was attempted.

SHA256:7108b97e9afb067689911c1817b6f9ebbc8fce97588a82bfd1a7f292708377e1.
Keep manifests, parent ELF, patches, proof and logs beside this image.
Physical10 A/10 B/10 A2 and>=20s continuous I2S/WebUI remain pending.
See docs/ESP8266_OPUS_ASM_PVQ_EXP2_WORD.md for the contract and reproduction.
