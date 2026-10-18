# Validate cached offsets against the current playlist

The [negative control](negative-stale-index.log) changes CSV row lengths while
retaining a correctly sized old index. The former loader accepts it; the new
test fails before the fix. Both targets now use one bounded row iterator for
construction and cache validation. Boot checks every offset in sequence against
the CSV and rejects missing/extra/mismatched entries before publishing a count.
Same-offset content changes remain valid. Raw Arduino uint32 index format and
direct indexed lookup are preserved.

[C3 index](c3/report.json) and [CYD index](cyd/report.json) execute actual
production functions under ASan/UBSan with real host stdio. They cover stale
offsets, embedded NUL, overlong row continuations/URLs, missing/final/empty rows,
out-of-range and non-boundary offsets, small URL destinations, malformed index
size and 65,536-row overflow, plus existing storage failure/recovery cases.

[Controller](controller/report.json) additionally proves both targets rebuild a
stale cache on boot, preserve a still-matching count after publication failure,
and disable mismatched offsets when replacement fails after a CSV change.
Files remain retained for recovery; a mismatched catalog cannot select a wrong
station. Existing pending/NVS/500-command regressions continue to pass.

Cache load now reads the CSV once in bounded memory instead of trusting only
index length; it avoids an unnecessary flash rewrite when the index matches.
Boot latency and physical SPIFFS durability require separate board measurement.
CSV/index upload transaction locking is subsequent stage 07 work.

Pinned SDK/GCC builds from clean `f75e7845` passed and were saved with matching
image/ELF/source/config hashes:
[CYD PDM](../../../firmware/development/esp32-cyd2usb-native-playlist-cache-pdm/manifest.json)
1,378,176 bytes; [C3](../../../firmware/development/esp32c3-oled-native-playlist-cache/manifest.json)
1,475,536 bytes. No physical test was performed. A subsequent pending-state
follow-up extends the HTTP startup regression; use its later image for testing
that complete connection-state behavior.
