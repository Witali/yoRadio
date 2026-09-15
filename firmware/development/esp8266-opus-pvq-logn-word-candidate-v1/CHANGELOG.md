# Experimental logN word-load candidate — 2026-09-15

Native ESP8266 Opus ASM raw benchmark, not production and not speed-qualified.
Parent: accepted pvq-index-half80.019979% CPU192; CPU160/QIO40 unchanged.
Replace one emulated signed16 flash load with phase-specific aligned32 ASM.
App903216 B; static RAM/IRAM and stack unchanged,24 host cases exact and
132416 linked numeric cases verified. No target upload: board unavailable.
All174 related regressions PASS/0skip; final-tests.log retains the full run.
Three failed status observations are saved; no serial recovery was attempted.

SHA256:2061c500bf801efd60e77286f5cbeb67cc3197cedcdfc373f929ebf314b8ceda.
Keep all manifests, parent ELF, patches, proof and logs beside this image.
Physical10 A/10 B/10 A2 and>=20s continuous I2S/WebUI remain pending.
See docs/ESP8266_OPUS_ASM_PVQ_LOGN_WORD.md for the contract and reproduction.
