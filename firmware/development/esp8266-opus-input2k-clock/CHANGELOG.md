# Opus input2048 diagnostic candidate, 2026-09-10

Source5147be3, app885520B. Same configuration as input1k-clock except Opus
input2048B. Fixed scratch6144B, minimum4096B post-init reserve, PCM and
2x512-word GPIO3 I2S PDM32 DMA unchanged. This requires1024B more dynamically
allocated DRAM; static sizes alone do not establish safe heap headroom.

Built and archived for A/B; no qualification is implied by compilation.
Do not promote before repeated physical continuity/heap measurements.
Builder changes remain diagnostic-only; production input stays1024B.
Host lifecycle tests include2048 input with allocation-failure and cleanup
coverage. They cannot prove free contiguous memory on the physical device.

Completed ten attempted DLF24 windows:0/10 pass. First health pair missing;
windows3..10 had no PCM progress. The device stopped with CONNECTION ERROR.
Their~2540 idle neutral-DMA events/window must NOT be read as decoder CPU
or as an audio-speed comparison against1KiB. [All results](comparison.json).
The DLF endpoint returned HTTP200 to a PC request; that does not prove an
uninterrupted device/Wi-Fi path.

2026-09-11 follow-up with own local SILK12 HTTP fixture: playback began,
then transport timeout/reconnect ended with DECODER INIT ERROR. Diagnostic
allocation stage8 recorded6144B scratch allocation failure with8600B free
CAP8 DRAM (reserve4096B). Unlike the earlier connection error, this is a
concrete failed allocation. Largest block was not exposed/measured; the
aggregate free count alone cannot establish allocatable contiguous space.
No larger-input default accepted. Restored1KiB image by OTA; no serial,
network-adapter, Wi-Fi credentials or playlist changes.
