# Entropy IRAM exchange diagnostic — 2026-09-14

Pinned full tell-inline ASM, unchanged arithmetic/C fallback. ec_decode,
ec_dec_update and ec_dec_bit_logp move to IRAM; task PDM32 packer moves to
flash. Cold __moddi3 stays in flash, DMA ISR stays in IRAM. Static IRAM−56B,
DRAM unchanged, app903152B. Exact PDM and linked-graph preflight passed.
CPU160/QIO40/cache16, raw RAM fixtures, output/profiling OFF. All30 A/B/A
physical runs completed: CPU192 medians88.115/126.044/88.114%, regression43.04%.
Rejected/default-OFF. PCM/scratch exact; DRAM min7660/8228/8176B, free stack1660B.
18 final regressions pass;19 other linked-size-changing CFG checked.
Ordinary radio restored OTA, HTTP/WS/playlist verified. Not production or
proof of70% CPU/live qualification. Full runs and maxima retained.
See docs/ESP8266_OPUS_ASM_ENTROPY_IRAM.md.
