# Coarse function profile, 2026-09-13

Diagnostic raw-only Opus GCC-ASM, CPU160/QIO40, source0c2b5851.904784B.
Only root, quant_all_bands, MDCT and FFT are wrapped; all other calls are
direct.110 original ASM object files byte-identical to matching control-v2.
Adds416B static DRAM, no static IRAM increase. No decoder arithmetic change.

Ten complete trials, exact PCM on five fixtures, no observation errors.
Final192kbps function profile:1200 frames /24s source audio. Bands self
67.487%, MDCT self9.073%, FFT7.389%, remainder16.051%. Inclusive rows overlap.
Mean root24450.47us, maximum CPU27004us, maximum wall31487us. These are
INSTRUMENTED durations, NOT ordinary-radio estimates.

Matched control-v2 task CPU median92.819% ->122.777% (+32.275% relative).
Even this coarse profile perturbs performance materially; attribution of
the overhead to timers versus layout/cache is not established. Do not
subtract speculative overhead or mix coarse and detailed self percentages.
Minimum sampled DRAM7748B over all cases, stack free1452B. See summary.json,
summary.md, all original reports, build-audit.json and ota.json.
This is not a successful70%-CPU or continuous-radio qualification.
