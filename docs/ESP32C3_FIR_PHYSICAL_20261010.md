# FIR hardware results, archived 2026-10-10

The 32-tap software resampler **fails physical playback acceptance** on the
tested ESP32-C3 configuration. Keep it disabled. Correct host PCM arithmetic
and complete short-file tails do not establish real-time performance.

These are the completed 2026-10-09 tests, archived after the interrupted work
session. Both firmware identities and the original failures are retained.
The control uses the integer PDM divider without software compensation; FIR
uses the same divider and the two experimental resampler options.

| Run | Requested observation | Mean CPU / output task | Decoded audio / elapsed time | Delayed DMA notifications | Runtime |
| --- | ---: | ---: | ---: | ---: | --- |
| Heavy FLAC, control | 90 s | 79.25% / 5.84% | 0.9983 | 23 | No recorded fault |
| Heavy FLAC, FIR | 90 s | 99.82% / 42.63% | 0.7816 | 1,546 | Task-watchdog events |
| HE-AACv2, FIR, growing TLS records | 600 s requested; observation interrupted after 49.09 s | 100.00% / 69.85% | 0.7052 | 972 | Timeout and task-watchdog events |

Figures use the saved post-warmup measurement windows; the incomplete AAC
window must not be interpreted as a ten-minute result. Notification counts
are driver diagnostics, not counts or lengths of audible interruptions.
DMA write-error counts are zero in those windows. CPU percentage has no
acceptance ceiling: watchdog events and failure to keep pace are the reasons
for rejection. The control's nonzero notifications also remain unresolved.

Original case results are control FLAC **6/6**, FIR FLAC **4/6**, FIR AAC
**3/5**. The short-file suite passes **62/62**, including warmup and Stop;
all **60** independently replayed HTTP/HTTPS rational output sample counts
match. Stop restores the tested idle heap; that does not invalidate the
in-playback failures.

The controller verified restoration of its original integer-clock quiet
image, settings, playlist and Wi-Fi at the end. The board was subsequently
updated to the [fractional-clock listening build](ESP32C3_PDM_LISTENING_20261010.md).
The user heard no noticeable difference with that hardware divider. It is
the preferred next qualification path because it requires no extra
per-sample resampling work to compensate the output clock.

All original evidence, frozen test helpers and an offline replay are saved
in [the physical archive](../tests/results/esp32c3-fir-physical-20261010/README.md).
Host quality and build results remain in [the FIR implementation report](ESP32C3_FIR_RATE_20261009.md).
