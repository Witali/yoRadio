# Reused Xiph inverse MDCT on a wide working grid

Converts exact floor1 products once to binary64 on a separate power-of-two
scale, then runs unchanged Xiph backward-transform bodies specialized to
binary64. Lookup and padded in-place working arrays belong to the caller.
There is no heap allocation, window/overlap, PCM conversion or decoder switch.

See the [design](../../../docs/CYD_VORBIS_TRANSFORM_DESIGN.md) for bounds and
remaining requirements. The generator mechanically checks every extracted
function byte against the pinned original source and retains [COPYING](COPYING).
