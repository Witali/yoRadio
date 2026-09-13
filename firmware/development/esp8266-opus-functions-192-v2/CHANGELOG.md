# Detailed function profile, 2026-09-13

Diagnostic raw-only Opus GCC-ASM, CPU160/QIO40, source e550ded3. Coherent
SDK runtime clock for CPU and wall scopes;14 selected external symbols.
Image905376B; adds416B static DRAM, no static IRAM increase. No production
algorithm or default changed. OTA preserves configuration and SPIFFS.

Ten complete trials, all five golden PCM hashes exact. Full function rows
retain the final192kbps fixture:1200 measured frames /24s source audio.
Matched control is functions-control-v1. Detailed profiling raises median
192kbps task budget92.876% ->169.046% (+82.011% relative): these function
shares and maxima are INSTRUMENTED, not estimates of production costs.
See summary.json/.md, original reports, host-pcm-regressions.json and ota.json.
Host PCM is exact for five streams and mixed-mode PLC/reset; host speed is
not a target speed measurement. A separate coarse profile follows.
