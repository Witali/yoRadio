# 2026-09-15 — two additional PVQ flash-byte probes

- Based on accepted pvq-byte-word,84.01121% raw CPU192.
- Read pre-split upper cost and first search probe with an exact aligned
  word leaf. Reuse existing unused code bytes; no table/heap/stack growth.
- 378304 search and79902 split-threshold linked cases exact, plus24 host
  PCM/state/PLC/reset/OOM scenarios through510kbps/120ms.
- Initial verifier missed the CALL0-only leaf; opt-in call traversal and
  negative tests added. Failure log retained; full proof rerun successfully.
- Pre-deployment127 related regressions PASS,0 failures/skips,134.70seconds;
  complete preflight-tests.log retained beside the image.
- All30 physical A/B/A complete. CPU19284.00988 /82.83819 /84.02250%,
  CPU12874.45779 /73.76998 /74.45352%; both high-bitrate gates PASS.
  Static RAM/frame unchanged; candidate free stack1660 B/minDRAM8028 B.
- Control A/run3 HTTP timeout/minDRAM544 B/CPU19296.92825% retained; PCM exact.
  Candidate192 max21.407ms, not a continuous-output guarantee.
- Ordinary live512-idle3s restored OTA; HTTP/WS/station/playlist checked.
  Default unchanged.80% CPU and live I2S PDM/WebUI remain outstanding.
- Final129 related regressions PASS,0 failures/skips,143.00seconds;
  final-tests.log includes independent physical-report/restore checks.
