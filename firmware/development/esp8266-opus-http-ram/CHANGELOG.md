# Diagnostic Opus HTTP RAM build — 2026-09-09

Source `9ebf42d`; app 910064 bytes, SHA-256 in `manifest.json`.
CPU160, QIO40, I2S PDM32 DMA GPIO3, 2 x 512 words; mono output.
Opus input1024, scratch6144, private-word ASM ON, raw benchmark ON.
SPIFFS log and HTTP log export OFF. Not a qualified production release.

Changes relative to the previous word-ASM test: SPIFFS slots10->5 save1620
DRAM bytes; shared HTTP scratch saves1536 BSS bytes. No reduction in audio
stack, DMA buffers, supported formats, or the 4096-byte allocation reserve.

Build and target IRAM/flash instruction guards passed. OTA passed from app0
to app1 (0x110000); no serial access, partition rewrite or playlist edit.
The real Intense 56-kbit/s stream now initializes successfully, with a
lifetime minimum heap4372. It still stops before PCM with `invalid Ogg stream`:
captured pages jump from saved header sequence1 to live audio sequence2534.
This binary does not yet contain a live-join sequence-baseline fix.

A fast local 64-kbit/s HTTP source still fails the allocation reserve gate:
free DRAM3400 versus required4096. More memory headroom is needed for that
receive-queue state. No claim of continuous playback is made.

Also archived: exact generic32 comparison of675 real CELT packets (648000
samples), scratch5488/6144; and the target fixed-point arithmetic audit.
No recorded music or credentials are included in these reports.
