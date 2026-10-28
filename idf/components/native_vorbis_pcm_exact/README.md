# S16 from complete exact window products

`native_vorbis_pcm_s16_product_pair` adds both independently scaled 106-bit
dyadics before nearest-even rounding and signed16 saturation. It preserves
large cancellation and an arbitrarily small nonzero half-tie perturbation.
Base exponents remain symbolic when bounded shifts are included, accepting
both signed64 endpoints without arithmetic overflow or floating scaling.

`native_vorbis_pcm_s16_windows` reads logical slices of two successful immutable
exact-window views. Out-of-whole-block indices are zero, including negative
origins. It preflights every selected read before output writes and needs no
materialized product arrays. Actual adjacent sizes determine the slices;
history ownership, priming, reset, granule trimming and flush policy remain
with the stream owner. Both inputs may share read-only storage; output is disjoint.

These APIs are exact for their supplied dyadics. They do not certify preceding
floor/IMDCT/curve approximation, complete codec conformance, radio resources,
or real-time performance. Existing APIs and production selection are unchanged.
See [the design](../../../docs/CYD_VORBIS_EXACT_PCM_DESIGN.md).
