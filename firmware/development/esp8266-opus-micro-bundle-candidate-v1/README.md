# Experimental Opus ASM micro-bundle

Three exact, disjoint overlays: ec_dec_bits + FFT load3 + sixteen signed16
MDCT products on the accepted PVQ baseline. 160 MHz / runtime QIO40.
Raw RAM-packet benchmark, no audio output; not production or live-qualified.
903216 bytes; static RAM/stack delta 0. Default and C fallback unchanged.

30 physical A/B/A runs: exact PCM, both high-bitrate gates FAIL.
CPU192 A/B/A2:87.32385 /87.31594 /87.31394%; no repeatable aggregate gain.
Not accepted as the new baseline; components retained for other combinations.
Ordinary radio restored OTA; HTTP/WS/station/playlist checked.

[Recipe, correctness and physical results](../../../docs/ESP8266_OPUS_ASM_MICRO_BUNDLE.md).
