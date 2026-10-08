# ESP32-C3: 1, 2 and 5 ms scheduler tick comparison

Date: 2026-10-08. ESP-IDF 6.1 pinned at
`9a97f6c54ec638111ce55cd36581b3c192f15207`.

## Scope and method

This is a physical comparison of the two heavy cases, not the full format
matrix. The baseline uses `CONFIG_FREERTOS_HZ=1000`; the experimental overlays
select 500 Hz (2 ms) and 200 Hz (5 ms). Saved sdkconfig values differ from the
baseline only in this setting. Source code, CPU/flash settings, output priority
8, decoder priority 7, stream priority 5, compact full-rate AAC, PCM/DMA buffer
sizes and TLS settings are unchanged. Embedded build version strings differ.

Each image runs these cases, in this order:

1. 60 seconds of FLAC 48 kHz, stereo, 16-bit over HTTPS, using
   `stress-flac-48000-2ch-16bit-610s`. The host sends the file without pacing,
   with 1024-byte writes and TLS 1.2 AES-256-GCM.
2. 90 seconds of HE-AACv2 44.1 kHz stereo, using `hev2-44100-stereo`, with
   alternating 1024/16384-byte plaintext TLS records and TLS 1.2
   ECDHE-RSA-AES128-GCM-SHA256.

Both cases retain idle-heap recovery, original runtime/heap gates, passive USB
telemetry and WebUI polling. CPU utilization is informational. Measurement
begins after ten seconds of warmup. CPU/decoder aggregates include only complete
intervals. DMA deltas cover the first through last selected counter samples,
not the entire nominal test duration. Builds finish before physical tests begin.

These are laboratory images with a test CA, experimental TLS RX reservation and
diagnostic logging. They remain **NOT_QUALIFIED** for production. The ordinary
root bundle and certificate validation remain enabled. The 1 ms baseline is the
previously recorded staged-DMA image; the two candidate images are installed by
native application OTA. Each controller restores the previous quiet image and
checks unchanged Wi-Fi, playlist, settings and playback state.

## Results

**Keep the current 1 ms default.** The 2 ms run shows a small CPU reduction
in HE-AACv2, but does not resolve the FLAC output failure. The 5 ms FLAC run
has more delayed DMA service and a larger real-time deficit. These are one
short run per image/case, not a repeated randomized experiment; small differences
must not be presented as a proven causal speedup.

| Case | Tick | Mean CPU busy | Decoded audio / wall time | DMA queue overruns / observed seconds | New watchdog events | Original playback/runtime gates |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| FLAC HTTPS | 1 ms | 100.00% | 0.96588 | 154 / 45.109 s | 11 | FAIL |
| FLAC HTTPS | 2 ms | 100.00% | 0.96708 | 145 / 45.109 s | 11 | FAIL |
| FLAC HTTPS | 5 ms | 100.00% | 0.95460 | 200 / 45.140 s | 11 | FAIL |
| HE-AACv2 HTTPS | 1 ms | 74.76% | 1.00158 | 0 / 75.110 s | 0 | PASS |
| HE-AACv2 HTTPS | 2 ms | 73.56% | 1.00156 | 0 / 75.109 s | 0 | PASS |
| HE-AACv2 HTTPS | 5 ms | 73.88% | 1.00161 | 0 / 75.093 s | 0 | PASS |

The FLAC decoded-audio deficit is respectively **3.41%, 3.29%, 4.54%**.
Actual written PCM gives comparable audio/wall ratios of 0.96525, 0.96714,
0.95466 (fixed 48 kHz stereo s16 output). Queue-overrun rates are 3.414/s,
3.214/s and 4.431/s. A queue overrun means a discarded completion notification;
it is not an exact audible-gap or missing-sample count. No acoustic/electrical
capture was performed. CPU saturation itself did not fail any gate: the FLAC
failures are retained watchdog events, accompanied by the measured output deficit.

CPU aggregates cover nine complete FLAC windows and fifteen complete AAC
windows per variant. DMA coverage is complete in every selected window;
there are no malformed/gapped CPU intervals or recorded allocation failures.
SDK write errors are zero. AAC keeps full 44.1 kHz stereo output in all runs.
Its CPU change relative to 1 ms is -1.20 percentage points at 2 ms and -0.88
points at 5 ms, with no observed DMA-overrun improvement because the baseline
already has zero overruns in this short AAC test.

| Case / tick | Minimum free heap / largest block | Median / minimum RSSI | Maximum status-request time |
| --- | ---: | ---: | ---: |
| FLAC / 1 ms | 57,564 / 38,912 B | -61 / -61 dBm | 140 ms |
| FLAC / 2 ms | 57,716 / 32,768 B | -56 / -56 dBm | 125 ms |
| FLAC / 5 ms | 57,312 / 34,816 B | -65 / -65 dBm | 140 ms |
| AAC / 1 ms | 26,136 / 17,408 B | -61 / -72 dBm | 141 ms |
| AAC / 2 ms | 26,224 / 18,432 B | -65 / -67 dBm | 141 ms |
| AAC / 5 ms | 26,284 / 18,432 B | -58 / -65 dBm | 140 ms |

RSSI and heap layout vary between sequential runs. This table preserves that
variation rather than attributing every small difference to the scheduler.
All idle-recovery gates passed. Both candidate OTA installations and both
restorations passed; the quiet image resumed the saved station with unchanged
Wi-Fi, playlist and settings. This short comparison does not supersede the
retained ten-minute AAC heap-trend failures or qualify long-term playback.

## What the tick change actually changes

FreeRTOS time slicing applies to ready tasks at the same priority. A higher
priority task can preempt when it becomes ready without waiting a complete
tick. Output and decoding have different priorities, so a 5 ms tick does not
give the decoder an uninterrupted 5 ms execution allowance.

The pinned SDK maps `configTICK_RATE_HZ` to `CONFIG_FREERTOS_HZ`, enables
`configUSE_TIME_SLICING`, and converts milliseconds to ticks using integer
division. This experiment intentionally preserves existing source delays:

| Existing operation | 1 ms tick | 2 ms tick | 5 ms tick |
| --- | ---: | ---: | ---: |
| `pdMS_TO_TICKS(1)` during decoder cleanup | 1 tick | 0 ticks | 0 ticks |
| `pdMS_TO_TICKS(5)` waiting for PCM | 5 ticks | 2 ticks (4 ms nominal) | 1 tick |
| 2 ms PDM bias-settle delay | 2 ticks | 1 tick | 0 ticks |
| `vTaskDelay(1)` every 32 decoder calls | 1 tick | 1 tick (2 ms nominal) | 1 tick (5 ms nominal) |

One-tick waits in AAC history ownership and OTA cooperation also change their
nominal duration. A zero-tick `vTaskDelay` yields without a timed block. Actual
one-tick blocking duration depends on where execution falls between ticks.
Thus this is a comparison of the complete firmware timing change, not an
isolated measurement of scheduler interrupt overhead. The zero-tick cases need
an explicit timing audit before adopting either larger tick as a default.

## Reproduction and evidence

Add `sdkconfig.freertos-tick-2ms.defaults` or
`sdkconfig.freertos-tick-5ms.defaults` **last** in the build defaults list and use
a fresh build directory/sdkconfig. Existing generated configuration can retain
the previous value. Check the final `CONFIG_FREERTOS_HZ`, not just the overlay.
Do not combine the two overlays.

The [evidence archive](../tests/results/esp32c3-freertos-tick-20261008/) retains
build recipes/logs, linked AAC/HTTP/TLS audits, source snapshots, exact image
identities and configurations, OTA/restoration checks, original physical
reports, transport traces and the comparison script. Its baseline references
point to the immutable [1 ms measurements](../tests/results/esp32c3-rxonly-long-20261008/staged/).
Private keys and generated audio are excluded. The saved laboratory certificate
has a limited lifetime; regenerate and embed test trust before a later rerun.

Images are saved under `firmware/development/` in the
`esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-tick2` and `-tick5`
directories. The production tick default remains 1000 Hz (1 ms).
