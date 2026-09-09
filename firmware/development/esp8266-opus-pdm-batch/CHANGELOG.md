# PDM32 batch on physical Opus — 2026-09-09

Source 4fa9043, 882848 bytes, OTA app1 to app0 passed. Same word-ASM,
PDM32 IRAM, WebAudioPause OFF, SPIFFS-cache OFF profile as the priority
control, with PDM batch ON and SDK RX counters OFF. No production default
was changed. Fixed-point Opus archive still has no soft-float/libm imports.

Host tests passed all 12 tests: bit-exact output/state/commit boundaries,
including 6480 blocks, 1841169 words and 5670 failure cases per mode.
No additional DMA buffers or PCM arrays are allocated by batch processing.

The physical sparse 27-second local SILK12 run FAILED. It decoded about
7 seconds after start, then latched RX timeout (result 4, errno 116),
followed by decoder reserve failure (stage 10, free DRAM 3736 vs 4096
required). Server TCP_INFO recorded actual retransmissions and RTOs.
This interrupted run cannot establish batch CPU speed or DMA improvement.
Keep this optimization opt-in pending an uninterrupted physical A/B.
