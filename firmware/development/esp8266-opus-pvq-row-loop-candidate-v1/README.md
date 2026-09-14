# Experimental PVQ row-loop ASM benchmark

160MHz, QIO40, raw RAM packets, no PDM output or stage/function profiler.
Not production and not proof of live-radio continuity. Parent: accepted
MDCT post-pair. Only35 bytes in decode_pulses replaced; RAM/frame unchanged.
See [experiment](../../../docs/ESP8266_OPUS_ASM_PVQ_ROW_LOOP.md)
for rationale, correctness checks and the pending10 A/10 B/10 A results.

Changelog 2026-09-14: reuse row[K] pointer, directly decrement pulse count,
remove one MOV and unconditional back-edge from each continuing probe.
Existing C fallback and immutable GCC snapshot remain untouched.
