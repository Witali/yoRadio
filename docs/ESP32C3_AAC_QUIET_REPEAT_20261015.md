# Quiet continuous-confirmation AAC HTTPS repeat

## Result

The requested 600-second public AAC-LC observation on the unchanged
`idf61-confirm-20261014` candidate **fails**. Independent replay finds **36 new
DMA completion-queue drops**, all between approximately 413.57 and 415.21 s.
There are zero write errors and no recorded allocation, decoder or watchdog
faults. The prior diagnostic image's passing ten-minute run does not qualify
this quiet image or establish why their results differ.

App SHA-256: `832ad10f31dbfa2aebe1b9b01012a4b2c4fab3a7bad75bfce45e3c7cc84375bb`.
ELF SHA-256: `30a89eacd0564a3264ff78da5578077778bf50d92bff51fed66787829f21eb43`.
No firmware source, configuration or DSP changes were made for this repeat.

## Measurements

| Measurement | Result |
| --- | --- |
| Original campaign checks | 6 PASS, 1 FAIL |
| Last playback observation | 599.663 s |
| First matching decoded format | 2.919 s, AAC-LC 44.1-kHz stereo |
| Independently selected steady window | 1,065 samples, 584.180 s |
| Completion drops / write errors | 36 / 0 |
| All retained health samples | 1,115, one boot |
| Minimum sampled free heap / largest block | 58,696 / 32,768 B |
| Settled free-heap median before / after Stop | 139,460 / 139,468 B |
| Settled largest block before / after Stop | 110,592 / 110,592 B |
| Settled tasks before / after Stop | 16 / 16 |
| Longest status/health observation | 201.786 ms |
| Playback RSSI range / median | -75 to -55 / -60 dBm |

The output increments are 19, 15 and 2 across three consecutive sampled
intervals. At those endpoints free heap is 63,192, 62,576 and 67,760 B;
the largest free block remains 32,768 B. These data do not identify network
starvation or scheduler delay. No acoustic continuity claim is made.

## Test finding: one failure hid another

The original runner reports `Progressive heap loss` and exits that case before
calling its output gate. Its raw health data nevertheless contain all 36
completion drops. The failed report is preserved unchanged.

The original memory window begins 15 seconds after the Play request starts;
the independent replay begins 15 seconds after the observation loop starts.
Those are slightly different boundaries. The latter passes the endpoint-median
memory check (63,920 to 62,440 B), but still fails the output gate. It must not
retroactively replace the original failed result. The original runner did not
save its precise window boundaries; future reports now save them explicitly.

Minute-wise free-heap medians remain between 63,270 and 63,664 B. Every minute's
largest-block median is 32,768 B, and stopped-state recovery passes. This does
not demonstrate a progressive leak, nor attribute the live allocations; it
shows why endpoint selection and all independent gates must remain visible.

The public runner now evaluates format, response time, memory, decoder faults,
output measurement and output acceptance independently, retaining every result
before raising the combined failure. Nonzero output counters remain available
even when memory fails. Initial format acceptance requires matching decoded
parameters rather than a provisional `audio=true`. Incomplete observations fail.
Five new regression tests and eleven existing idle/output tests pass. Thresholds
are unchanged; failures are not waived.

## Restoration and next step

The app-only OTA controller restored `idf61-prod-20261013` on app1, verified
the expected ELF hash and unchanged Wi-Fi/playlist/settings, and stopped playback.
The failed campaign, independent per-gate replay, minute statistics, controller
and source hashes are [archived](../tests/results/esp32c3-confirm-quiet-long-20261014/physical/).

Reproduce with controlled TLS delivery and bounded phase/checkpoint recording;
then compare a targeted change against the same delivery schedule. Do not raise
output priority or production buffer limits solely from this aggregate counter.
The separate FLAC/WebUI TCP-connect timeout also remains open.
