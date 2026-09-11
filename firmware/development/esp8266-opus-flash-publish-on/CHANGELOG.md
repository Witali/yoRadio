# Opus flash-output publication candidate

2026-09-11, source eee18c2, app903808B. Diagnostic only, not a release.
Same settings and five fixtures as ../esp8266-opus-flash-publish-off,
except publication ON. Both raw and radio payload algorithms are unchanged;
the benchmark now publishes every successful PCM callback's pending tail,
matching the experimental radio path. No extra PCM buffer or padding.

Host lifecycle tests passed with ASan/UBSan: five allocation failures,
cancellation, exact expected PCM, write/publication errors and repeated
cleanup. Matched application hashes verified. Ten physical attempts completed;
comparison.json retains all ten OFF and ten ON reports. No runtime bitrate
limit is introduced.

ON passed the digital continuity gate only for SILK12 (10/10 versus9/10 OFF).
All24/64/128/192-kbit windows failed. Median pipeline CPU percentages are
36.781/68.322/78.781/88.675/97.622; median DMA misses0/35/53/231.5/829.
Thus the small reduction in CPU does not establish a continuous-output fix;
128-kbit misses increased from168.5 to231.5. Publication remains default OFF.

All measured PCM hashes/counts match. Lowest per-case free DRAM:
7140/1732/1572/500/500B. Lifetime heap minimum reached192B on attempt3;
subsequent192B snapshots are not separate low-water events. Observation
errors on attempts1/2/3/4/10 are retained, not replaced by new attempts.
The whole candidate fails the continuity and memory gates. FIFO empty=0
does not exclude neutral-word fallback. No analog capture was made.

Both series used30s status polling. Host regression tests and compilation
of the next experiment ran during parts of ON; this was not an interleaved
or host-load-isolated experiment. Wi-Fi/system activity remains a factor.
Do not interpret small median differences as guaranteed instruction speedups.

21 local PCM/PDM/lifecycle/profile regressions passed after the series began;
the saved reports have an additional reproducible evidence test. See
../../../docs/ESP8266_OPUS_PCM_PUBLICATION.md for the full comparison.
