# Fragmented public Ogg/Opus output-resize probe

The complete 120 ms fixture first reproduces the unchanged public vendor baseline
with 24576-byte output capacity. Independent 4096, 257 and one-byte streams then use
the exact production pending/EOF headers, separate caller EOF, initial 12288-byte
capacity and current resize-then-retry-unchanged policy. Real BUFFER_NOT_ENOUGH
fields, complete byte/PCM identities and cleanup are recorded.

A failed current stream or nonzero consumption on resize triggers a separate
fresh honor-consumed strategy, permitting an empty-input PCM retry after resize.
Unsupported outcomes remain explicit; matching output without a real resize
event does not qualify resizing. Decoder worker placement remains core 1,
priority 3, stack 16384, with watchdogs, assertions, canaries and heap checks.
No production source, private codec ABI or hardware is used. Diagnostic images
must not be flashed as radio firmware. Required playback trimming remains open.
