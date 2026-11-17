# Warning review

Each CYD profile adds three occurrences of
`bugprone-suspicious-string-compare` to the November 11 catalog. They
refer to `memcmp` results used as Boolean mismatch checks in the Opus
header and channel-policy readers. A nonzero result is the intended
condition in each expression.

Both legacy profiles also report the existing PCM speaker-mix diagnostic.
The trace assumes the reader has zero channels while the prepared mono
weights have a nonzero channel count. The output owner prepares those
counts together and only uses a valid reader. The same diagnostic
already occurs in the PDM and continuous profiles. The existing
surround/gain tests cover channel permutations, silence and rounding.
[Speaker-mix preparation](../../../idf/esp32-cyd2usb-native/main/native_audio_output.c)

The C3 production console policy adds five dead-store diagnostics for
values used only by disabled log calls. Other warning classes match the
previous C3 catalog.

The inherited Ogg event warning follows an analyzer path that returns a
positive sticky fault without writing an event. The timeline stores
negative error statuses in that field. Its allocation warning refers to
page storage retained by the owner until ACK/reset/abandon. The existing
allocation-refusal, ownership and sanitizer cases exercise those paths.
The HTTPD context-cleanup warnings retain the prior review.
[Previous warning review](../cyd-production-matrix-20261111/WARNING_REVIEW.md) · [Full current sites](clang-warnings.json)
