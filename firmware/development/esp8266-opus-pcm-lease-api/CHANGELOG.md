# Diagnostic PCM lease API ON compile check

2026-09-11, source136a6a1, app885728B. Matches pcm-lease-off except explicit
`-OpusPcmLeases`. No bridge/consumer integration yet: normal radio still uses
the synchronous output callback. This binary must not be described as a
working asynchronous PCM queue, and has NOT been flashed or timed on hardware.

Host two-slot simulation passes12 exact PCM comparisons including a retained
real-radio fragment. Fault/cancellation/OOM ownership cleanup is tested.
Against API OFF: flash text+204B, rodata+4B, all static RAM sections equal;
DMA ISR387B and identical section hash. This is not a codec-speed measurement.
See docs/ESP8266_OPUS_PCM_QUEUE.md for the remaining integration and gates.
