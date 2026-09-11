# Opus PCM publication control

2026-09-11, source c9728ad. Diagnostic control,885520B, same settings as
the paired ON profile except `opus_pcm_publish=false`. Input1024B,
scratch6144B, CPU160/QIO40 and GPIO3 standard I2S PDM32/two512-word DMA.
No claim of gap-free playback. Intended for ten physical attempted windows
per variant on the same own Opus fixture, retaining all failures.
See [methodology](../../../docs/ESP8266_OPUS_PCM_PUBLICATION.md).

Ten attempts completed,0/10 qualified. Complete health pairs only1..4;
missing5..10 retained, POST starts4/8 unconfirmed (no response files).
Misses in observed windows956/2289/11/9. No outliers were removed.
See paired comparison.json in ../esp8266-opus-publish-on/ and local-tcp.jsonl.
This control binary is retained for reproduction, not as a gap-free release.
