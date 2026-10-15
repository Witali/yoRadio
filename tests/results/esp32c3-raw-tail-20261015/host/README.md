# Opaque FLAC/Ogg tail coalescing regression

`before` reproduces the packing failure on source commit 15de0c36. The captured
old router header and generated test unit are retained. `after` is the first
passing implementation, before the additional inter-call cancellation guard.
`after-cancel` tests the final implementation, including restoring an old queued
prefix if a generation changes between feeds. The final tests also cover
FLAC/Ogg codec/generation/EOF/drain barriers, eight 512-byte reads in three slots,
and 600,000 exact bytes with concurrent ownership transfers under ASan/UBSan.

`staging` verifies four held startup slots and a concurrent consumer; `start`
executes the actual send/finish paths with frame confirmation and queue pressure,
including FLAC/Ogg passthrough. These are host control-flow/byte-identity tests,
not decoder quality or hardware playback evidence.
