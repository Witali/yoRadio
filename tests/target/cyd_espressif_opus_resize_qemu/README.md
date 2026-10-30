# Public Ogg/Opus output-resize probe

This isolated ESP32 LX6 / SDK 6.0.2 QEMU probe uses the unchanged public vendor
decoder and the valid 120 ms stereo fixture. The first fresh decoder establishes
complete raw PCM with 24576-byte output storage. Two independent fresh decoders
then start at the production 12288 bytes: one retries the same input after
BUFFER_NOT_ENOUGH, while the other advances by the public raw.consumed value.
Every resize logs the public input/output fields before making that choice.

Decoder errors, incomplete drain and PCM mismatch remain explicit unqualified
outcomes, with real close/free and heap checks. Finishing observations does not
make an unsupported retry strategy pass. Output on BUFFER_NOT_ENOUGH is logged
but not assumed valid PCM. No private ABI or hardware is used. Worker placement
is core1, priority3, stack16384; watchdogs, assertions and canaries remain enabled.
These diagnostic images must not be flashed as radio firmware. Opus pre-skip
and end trimming remain a separate unresolved playback correctness requirement.
