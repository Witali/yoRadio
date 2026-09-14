# Experimental ec_dec_bits low-bit extraction

Changelog2026-09-14: saved GCC ASM tail uses window XOR (high<<bits),
14→13 instructions,33 live bytes in original35-byte tail. SAR/entropy state
and call0 ABI preserved; only a5/a9 caller-saved scratch may differ.
No RAM/frame growth; accepted PVQ row-loop parent,160MHz/QIO40/raw RAM input.
81120 linked numeric cases and24 host exact PCM scenarios pass.
Not production; physical30 A/B/A and speed selection pending.
See [experiment](../../../../docs/ESP8266_OPUS_ASM_EC_BITS.md).
