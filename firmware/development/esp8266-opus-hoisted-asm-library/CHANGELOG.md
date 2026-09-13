# Opus invariant-SAR experiment

Standalone fixed-point GCC8.4/LX106 call0 library based on the same full
GCC snapshot as esp8266-opus-asm-library. Only vq.c.s is replaced; entropy
decoder uses unmodified GCC code. Optional backend: hoisted-asm.
No extra RAM/stack; two loop-invariant SAR writes move before their loops.
10000 snippet states match exactly; physical qualification remains pending.
See docs/ESP8266_OPUS_ASM_BOARD_ABBA.md for the70% CPU target, full previous
A/B results and limitations. COPYING/AUTHORS retain upstream attribution.
The archive is not an app image and its size is not linked flash consumption.
