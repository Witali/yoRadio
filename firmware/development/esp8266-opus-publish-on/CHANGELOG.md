# Opus PCM publication candidate

2026-09-11, source c9728ad. Diagnostic only,885648B. Opus input1024B,
scratch6144B, CPU160/QIO40, GPIO3 standard I2S PDM32, two512-word buffers.
WordASM/ICDF/FIR and PDM32 IRAM/batch enabled. No reciprocal experiment,
rotation ASM or decoder-only CELT. Only Opus PCM publication differs from
the paired OFF profile. No extra audio buffer or altered PCM/PDM algorithm.

Host producer/output matrix passed; no physical qualification implied by
compilation. Experimental flag remains default OFF. Full methodology:
[PCM publication experiment](../../../docs/ESP8266_OPUS_PCM_PUBLICATION.md).
The manifest and app.bin are the build artifacts; no SPIFFS/credentials included.

OTA passed. Ten attempts completed with all starts confirmed;3/10 health
windows qualified (4/6/9,28.2/29.0/28.0seconds). Windows3/5/7/10 lack health
pairs; observed failures1/2/8 have2/566/848 DMA misses. All are retained.
This is promising for output publication but not qualified radio playback.
The real56-kbit Opus follow-up failed, with transport timeout116 and then
stage10 reserve rejection (free3284B below4096B), not a4096B malloc failure.
Status/diagnostics/stop.json and local-tcp.jsonl preserve the observations.
Publication remains default OFF. See comparison.json and the linked document.
