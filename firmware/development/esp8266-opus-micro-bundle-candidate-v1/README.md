# Experimental Opus ASM micro-bundle

Three exact, disjoint overlays: ec_dec_bits + FFT load3 + sixteen signed16
MDCT products on the accepted PVQ baseline. 160 MHz / runtime QIO40.
Raw RAM-packet benchmark, no audio output; not production or live-qualified.
903216 bytes; static RAM/stack delta 0. Default and C fallback unchanged.

[Recipe, correctness and physical results](../../../docs/ESP8266_OPUS_ASM_MICRO_BUNDLE.md).
