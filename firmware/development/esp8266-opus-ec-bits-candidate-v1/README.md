# Experimental ec_dec_bits low-bit extraction

Changelog2026-09-14: saved GCC ASM tail uses window XOR (high<<bits),
14→13 instructions,33 live bytes in original35-byte tail. SAR/entropy state
and call0 ABI preserved; only a5/a9 caller-saved scratch may differ.
No RAM/frame growth; accepted PVQ row-loop parent,160MHz/QIO40/raw RAM input.
81120 linked numeric cases and24 host exact PCM scenarios pass.
Not production. Changelog2026-09-14: all30 A/B/A raw attempts complete;
CPU19287.35529 /87.32860 /87.33156%, but128 regresses in both comparisons.
Both high-bitrate speed gates FAIL: candidate REJECTED, default unchanged.
PCM exact, no RAM/frame growth; minimum DRAM8352 /8160 /8176 B.
All attempts/maxima and A2/run4 timing-window excess341us retained.
Ordinary firmware restored by OTA; HTTP/WS/playlist checked. No live qualification.
Final selected regression suite:65 PASS,0 failures,0 skipped; regression-final.log.
See [experiment](../../../docs/ESP8266_OPUS_ASM_EC_BITS.md).
