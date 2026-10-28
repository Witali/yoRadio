# Adjacent Vorbis blocks with independent scales

`native_vorbis_overlap_init` borrows the two prepared window lookups and reserves
caller storage for the unwindowed right half of the largest block. The first
`push` primes history without producing samples. Each later push produces
`(previous_size+current_size)/4` pairs of windowed contributions and replaces
history with the current unwindowed right half. `reset` discards history
logically; it does not clear or read the old sample bytes.

The two output descriptors retain their own signed64 exponents. Add and round
both terms together at the PCM boundary. Clipping each separately or aligning
them prematurely can lose cancellation or change a rounding half tie. Caller
storage and state are disjoint; consume outputs before reusing their arrays,
and serialize state use. There is no allocation, task or implicit flush.

Window multiplication is approximate binary64 arithmetic. It can underflow
before the retained scale is applied; downstream exact addition cannot recover
such lost terms. This stage therefore does not establish full-range decoder or
PCM accuracy. Granule/EOS trimming, floor0 domains/wider synthesis, raw/radio
lifecycle and native/resource qualification remain separate work. See
[the design](../../../docs/CYD_VORBIS_OVERLAP_DESIGN.md).
