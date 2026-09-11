# Opus flash-output publication candidate

2026-09-11, source eee18c2, app903808B. Diagnostic only, not a release.
Same settings and five fixtures as ../esp8266-opus-flash-publish-off,
except publication ON. Both raw and radio payload algorithms are unchanged;
the benchmark now publishes every successful PCM callback's pending tail,
matching the experimental radio path. No extra PCM buffer or padding.

Host lifecycle tests passed with ASan/UBSan: five allocation failures,
cancellation, exact expected PCM, write/publication errors and repeated
cleanup. Matched application hashes verified. Physical comparison pending;
do not claim performance from compilation or these host lifecycle stubs.
Ten attempts are required; no runtime bitrate limit is introduced.
