# Actual Ogg playback wrapper on ESP32

This diagnostic compiles the actual new `ogg_playback.h` and shared page,
timeline, pending-input and PCM-span owners against unchanged public Espressif
decoding. It is a prerequisite for production task selection, not the complete
radio/TLS/output-task pipeline. Public linker observers forward identical
arguments/results and hash raw PCM before the wrapper's real trimming callback.
Every decoder input page must already be CRC-verified.

Full Opus20/Opus120/Vorbis fixtures run through whole/4096/257/one-byte input.
Opus playback must match the independently retained vendor emission-position
window; Vorbis remains byte-exact to the full prior reference. Additional cases
cover pre-skip512 with positive64-bit granule offsets, genuine per-link EOS
drain/close/ACK ordering, suffixes from the next link within the same input,
Opus/Vorbis/Opus chaining, actual resize and a CRC-invalid audio page that never
enters the vendor decoder. Host seams independently exercise allocation,
cancellation, retained prefixes, error-consumed resize retries and output faults.

Images remain local diagnostic artifacts and must not be flashed as radio
firmware. No hardware, external network or private decoder ABI is used.
