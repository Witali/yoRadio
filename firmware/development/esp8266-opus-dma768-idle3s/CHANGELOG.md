# Diagnostic Opus DMA768 with3s receive inactivity deadline

2026-09-11, source ce19b93, app885536B. CPU160/QIO40, GPIO3 I2S PDM32,
two768-word DMA buffers, input1024B/scratch6144B. C rotation, word/ICDF/FIR
helpers, PDM batch/IRAM, SDK RX diagnostics. No PCM consumer queue.

Same firmware sources as the1s DMA768 control; the build-helper change sets
CONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS=3000. This is an inactivity deadline,
not a3s blocking read; cancellation checks and existing refill logic remain.
OTA succeeded, slot0x110000. Physical qualification0/10, all attempts retained.
No startup status was obtained; some later health snapshots show stopped PCM
and receive timeout116. This does NOT demonstrate that every start failed,
but it does not meet continuous20s playback or WebUI-response qualification.
The longer timeout alone did not fix the problem. Afterwards the saved512
control was restored by OTA. This binary is diagnostic, not a release.
