# Diagnostic PCM lease API OFF control

2026-09-11, source136a6a1, app885520B. CPU160/QIO40, standard GPIO3 I2S
PDM32, two512-word DMA buffers, input1024B/scratch6144B, idle deadline3s.
PCM leases OFF; existing synchronous output. No PCM consumer task/ring.

This target build checks removal of the experimental acquire branch/wrappers.
Static RAM sections and DMA ISR hash match the earlier512 control. Header/
timeout/app metadata may differ; equal sections are not full-binary equality.
Saved for reproducibility, not flashed and not hardware-qualified. The longer
deadline was not proven to fix live-radio stalls in the previous DMA768 series.
