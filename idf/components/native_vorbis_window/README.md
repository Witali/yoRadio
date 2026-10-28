# Vorbis window for scaled transform blocks

`native_vorbis_window_prepare` constructs one rising half-window in caller
storage. `native_vorbis_window_shape` places the short/long transition slopes;
`native_vorbis_window_apply` applies them to a full transform block and retains
its separate signed64 scale exponent. Both plans can reference the same lookup
when their sizes match. No trigonometry or allocation runs during application.

The window is the Vorbis I nested sine function. Coordinates follow the pinned
Xiph reference implementation, including trailing zeros beginning at the end
of the descending slope. The published specification's step8 names its start,
contradicting the preceding slope step; see the linked design discussion.

The component is independent of task placement, display and audio backends.
It is not selected by the production component lists. Overlap history, adjacent
block exponent handling, granule trimming, PCM conversion and decoder lifecycle
remain separate integration work. See
[the design](../../../docs/CYD_VORBIS_WINDOW_DESIGN.md) and
[host qualification](../../../tests/results/vorbis-window-20261028/CHECKPOINT.md).
