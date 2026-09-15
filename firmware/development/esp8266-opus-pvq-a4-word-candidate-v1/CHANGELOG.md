# 2026-09-15 — two additional PVQ flash-byte probes

- Based on accepted pvq-byte-word,84.01121% raw CPU192.
- Read pre-split upper cost and first search probe with an exact aligned
  word leaf. Reuse existing unused code bytes; no table/heap/stack growth.
-378304 search and79902 split-threshold linked cases exact, plus24 host
  PCM/state/PLC/reset/OOM scenarios through510kbps/120ms.
- Initial verifier missed the CALL0-only leaf; opt-in call traversal and
  negative tests added. Failure log retained; full proof rerun successfully.
- Pre-deployment127 related regressions PASS,0 failures/skips,134.70seconds;
  complete preflight-tests.log retained beside the image.
- No speed claim or default change until10 A/10 B/10 A completes.80% CPU
  and live I2S PDM/WebUI remain separate, outstanding requirements.
