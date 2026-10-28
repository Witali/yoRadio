# Granule positions and ready-span trimming

This independent integer metadata layer follows Vorbis I appendixA.2 and Xiph
block synthesis bookkeeping. First audio blocks prime; first known positions
trim the beginning, except a first-known EOS trims the end. Later EOS anchors
can trim only currently ready samples. Position mismatches resynchronize without
inventing data. Packet sequence gaps and hard restarts are distinct operations.

Wire positions are signed64 with-1 unknown. Internal counters saturate only
beyond INT64_MAX+4096, where every possible bounded trim is unchanged. A prediction
outside the signed wire domain is reported explicitly rather than narrowed.
No floating arithmetic, allocation, PCM/overlap execution or production selection
is introduced. The stream owner still coordinates decoded data, pending output,
transport continuity and logical links. See
[the design](../../../docs/CYD_VORBIS_TIMING_DESIGN.md).
