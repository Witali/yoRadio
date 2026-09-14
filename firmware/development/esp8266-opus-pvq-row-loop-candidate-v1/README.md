# Experimental PVQ row-loop ASM benchmark

160MHz, QIO40, raw RAM packets, no PDM output or stage/function profiler.
Not production and not proof of live-radio continuity. Parent: accepted
MDCT post-pair. Only35 bytes in decode_pulses replaced; RAM/frame unchanged.
See [experiment](../../../docs/ESP8266_OPUS_ASM_PVQ_ROW_LOOP.md)
for rationale, correctness checks and the completed10 A/10 B/10 A results.

Changelog 2026-09-14: reuse row[K] pointer, directly decrement pulse count,
remove one MOV and unconditional back-edge from each continuing probe.
Existing C fallback and immutable GCC snapshot remain untouched.

Physical result: CPU19287.46700 /87.30769 /87.49450%, both high-bitrate
gates PASS. Accepted experimental raw baseline;70% not reached. All30 PCM
hashes exact, no RAM/frame/scratch growth. All outliers retained, including
candidate run7 DRAM3816B and repeated-control run4 timeout/DRAM1400B.
Ordinary160MHz/QIO40/I2S PDM radio restored OTA and HTTP/WS verified.
Final46 related regression tests PASS/0skip; see regression-final.log.
