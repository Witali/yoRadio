# Opus optimized ASM candidate v1 — 2026-09-13

Same diagnostic raw-only benchmark configuration and fixtures as gcc-asm-v1.
Only ec_dec_update is changed from the GCC snapshot: joined normalization paths,
loop-invariant packet pointer, register-held state, no local stack frame.
Host instruction-model PCM is exact; full firmware links. No measured device
CPU improvement is claimed. NOT flashed, not production/default normal radio.
Snapshot/overlay/config/image hashes are in manifest.json; detailed tests and
static memory comparison are in ../esp8266-opus-asm-library/.
