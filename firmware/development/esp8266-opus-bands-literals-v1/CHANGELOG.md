# Experimental Opus ASM bands text literals

2026-09-13; source e583928e. Not production default or live-qualified.
Pinned tell-inline ASM, only bands compiled with --text-section-literals.
CPU160/QIO40, raw RAM packets, no audio output or function/stage profiler.
903184 bytes, SHA256 9cc40b51d5cbe83b4266ae2ed5ab5514b4b589104474d65d1b7a406e3f97e1ec.
The normal C fallback and production defaults are unchanged. OTA only.

46 regression tests PASS; parent host PCM/PLC/reset/OOM PASS. All eight linked
bands functions plus ec_tell_frac/ec_dec_bits have exact normalized instruction
graphs. Static RAM unchanged; flash text/image 32 bytes smaller.

All 30 physical A/B/A attempts complete, exact PCM, no observation errors.
CPU192 median: A 88.124708%, B 88.902604%, A2 88.097188%. B is 0.883/0.914%
slower than the controls; all five bitrates regress. Candidate rejected, flag
stays OFF. Full CPU/wall/heap/stack data and every run are in comparison.json.
Normal radio restored by OTA (restore-radio.json); WebUI root HTTP200 in
0.104889 s. This is smoke verification, not continuous-audio qualification.
The 70% CPU192 target remains unmet.
