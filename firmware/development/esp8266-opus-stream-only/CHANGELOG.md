# Opus stream-only baseline — 2026-09-09

Source 5c4391f, 881056 bytes; SHA-256 and effective configuration in manifest.
CPU160/QIO40, mono I2S PDM32 GPIO3, two 512-word DMA buffers, stacks 5120.
Opus word ASM ON, input1024/scratch6144, SPIFFS cache OFF. Raw benchmark,
FreeRTOS runtime/trace/formatting and SPIFFS logs OFF; stream test API ON.
PDM packer still in flash; no PDM32 IRAM experiment in this baseline.

Changes: stream diagnostics no longer carry raw benchmark overhead; an
existing Opus workspace can survive a recoverable transport reconnect.
Host tests and target IRAM/flash instruction guards passed. OTA app0→app1
passed without changing SPIFFS, Wi-Fi or playlist.

Local 40-second synthetic stereo64 Opus started decoding successfully,
but stopped after 153288 output frames (160 packets minus pre-skip312).
The 25-second continuity check FAILED: repeated four-second HTTP health
timeouts, stalled PCM, DMA underruns. Final stage8 failed to allocate6144
scratch bytes despite8404 total free DRAM; lifetime minimum heap4416.
This is not a qualified continuous-playback firmware. Reports retain all
timeouts and failed samples; do not infer success from initial playing=true.

Next investigation: blocking TCP connect during retry and flash execution
cost of PDM. No board speed improvement from IRAM placement is claimed here.
