# Exact PCM from two scaled binary64 terms

`native_vorbis_pcm_s16_pair` converts the sum of two independently scaled terms
to nearest-even signed16 PCM, then saturates. It never first materializes either
large/small physical floating value, clips an individual contribution, or loses
a tiny term that decides a rounding tie. Its exact dyadic comparisons work with
every finite binary64 value and both full signed64 scale exponents.

Caller capacities and all finite values are checked before output writes.
Inputs/descriptors remain immutable, with output in disjoint caller storage.
No heap, VLA, `__int128`, floating-rounding assumption or task is introduced.

This boundary is exact for its supplied terms. It does not prove accuracy of
prior floor/IMDCT/window computations, granule trimming, native timing or radio
integration. Production component lists and task placement remain unchanged.
