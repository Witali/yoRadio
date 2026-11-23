# Warning comparison

All six current Clang-Tidy runs complete with zero errors. Each profile's
file, check, message and occurrence count is exactly equal to the
[November 17 reviewed catalog](../cyd-ogg-word-production-20261117/clang-warnings.json).
Locations may move with source lines. No new or removed diagnostic is hidden
by comparing only total counts.

The per-profile warning counts remain 100/98/99 for PDM/continuous/legacy,
with either vendor or custom FLAC. This is 594 warning occurrences across
320 project units, plus 20 successful SDK frontend checks. The 13 typed
compiler/libc configuration differences are the same as before.

The [previous warning review](../cyd-ogg-word-production-20261117/WARNING_REVIEW.md)
still applies; this result is not a claim that every existing warning has
been eliminated. Full current [sites](clang-warnings.json), report identities,
configuration identities and image/ELF bindings are in [the matrix](matrix.json).
