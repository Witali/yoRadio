# Asymmetric AAC owner: physical qualification

## Build and exact decoder checks

`CONFIG_YORADIO_AAC_ASYMMETRIC_OWNER` enables the
[audited asymmetric owner](ESP32C3_AAC_ASYMMETRIC_OWNER_20261003.md) in ordinary
firmware. It depends on the scoped low-QMF option and remains **off by default**.
Use `sdkconfig.aac-asymmetric-owner.defaults` for the complete dependency chain.
The owner requests 32,744 instead of 35,900 bytes; the measured QEMU allocator
block falls from 36,864 to 32,768 bytes. The existing 16 KiB decoder stack,
all AAC output rates/channels and native SBR/PS calculations are retained.
This step adds no quantization to the preceding PC18 configuration.

The production storage path passed all six QEMU runs without transient-row
poisoning: 657,540 synthetic channel samples are bit-identical and the five
complete recordings retain their PCM hashes and 12,505,088 channel samples.
There are 2,583,444 pointer/range checks, 161,368 SBR copies, 929 allocations
matched by 929 frees, and 4,845 scoped low-QMF matrices. Minimum concurrent
decoder stack margin remains 2,844 B. These are function-boundary ownership
checks, not instrumentation of every native load/store. The existing
unchanged-header implicit SBR/PS restart limitation is unchanged.

The physical configuration differs from the previous low-QMF firmware only
by the new flag. It keeps DIO 80 MHz, disables deep sleep and Flash Auto Suspend,
and excludes QEMU/audit symbols. The old symmetric native initializer is not
linked; the typed initializer is linked. The compiled scoped wrapper still
uses a 10,304-byte frame.

The saved development image is
[`firmware/development/esp32c3-aac-asymmetric-owner`](../firmware/development/esp32c3-aac-asymmetric-owner/manifest.json),
ELF SHA-256 `7a08ff29d13eed4ffa987bfe93b86808a2fead6bc3f1ae41a389e506963dfcb1`.
It is an experimental image, not a versioned release.

## Baseline failures remain recorded

Before installing the candidate, the prior low-QMF image initially reported
`stream read failed`. The first controlled load run passed LC but lost WebUI
connectivity during HE; HEv2 and restoration also failed with `URLError`.
The board became reachable again without a reset. At that later observation,
it still reported `stream read failed`, and a direct TCP connection succeeded.
No cause is assigned from those observations alone.

In a separate baseline repeat, HE and HEv2 passed, as did restoration. LC
failed the existing maximum WebUI response-time criterion of two seconds.
Both attempts are retained. The incomplete first run has insufficient CPU
samples for a complete comparison; it is not presented as a passing benchmark.
The repeat provides diagnostic 5..35 s windows, with original PASS/FAIL outcomes.

The runners now retain nested exception types and numeric `errno`/`winerror`
values, without exception messages, URLs or credentials. Failures still fail;
no retry or acceptance relaxation is introduced by this diagnostic change.

## Initial physical comparison

The initial OTA transition during controlled AAC-LC playback passed in 21.390 s.
The new running hash and unchanged Wi-Fi, settings and playlist were verified.

The table uses the same diagnostic 5..35 s CPU window after first PCM. The
candidate HE window is partial because its WebUI request timed out after
30.984 s. These numbers do not override the failed acceptance outcomes.

| Case | Acceptance before / after | Decoder CPU before / after | Whole-radio CPU before / after | Minimum free heap before / after | Largest free block before / after |
| --- | --- | ---: | ---: | ---: | ---: |
| LC 48 kHz stereo | FAIL / PASS | 19.133 / 19.333% | 44.017 / 46.883% | 75,156 / 76,644 B | 49,152 / 57,344 B |
| HE 48 kHz stereo | PASS / FAIL (timeout) | 38.217 / 38.175% | 61.383 / 61.800% | 37,176 / 42,836 B | 14,848 / 32,768 B |
| HEv2 44.1 kHz stereo | PASS / PASS | 42.667 / 42.817% | 66.483 / 66.233% | 37,448 / 43,096 B | 14,848 / 32,768 B |

Both logs have no captured allocation/decoder/panic error. Minimum sampled
decoder stack margin is 2,828 B before and 2,716 B after, from the same 16 KiB
stack. Only the HEv2 pair passes both load tests. Network allocations and RF
conditions vary, so sampled heap differences are not an exact measurement of
the owner saving, and partial windows do not establish a speed guarantee.

During the subsequent HTTPS matrix the user repositioned the board. A
five-sample probe at 10:04:04 UTC returned RSSI values −58, −72, −72, −58, −58 dBm;
all five reported HE-AAC playback and USB remained available. This matrix
therefore has mixed RF conditions. The one-off probe's `request_ms` values were
mistakenly sampled before making the request and are explicitly marked invalid;
they are excluded from latency conclusions. The suite's separate request
timings are measured after each response and remain valid.

## Public HTTPS matrix with mixed reception conditions

Four of five 60-second playback cases pass: AAC-LC 128 kbit/s, HE-AAC
32 kbit/s, HE-AACv2 16 kbit/s and MP3 256 kbit/s. HE-AAC 64 kbit/s fails the
existing progressive-free-heap criterion. There are no captured allocation,
decoder, TLS or panic errors in this matrix. Idle recovery and restoration pass.
The previous image's recorded 1,700-byte allocation failures did not recur
in this bounded run; this does not prove they cannot recur under other loads.

In the failed 64 kbit/s case, the first three steady-window free-heap readings
are 22,472 / 24,172 / 27,756 B, and the last three are
20,584 / 24,420 / 20,452 B. Their medians differ by 3,588 B, exceeding the
unchanged 2,048 B gate. The values fluctuate; this check alone does not identify
a leaking allocation or its owner. The smallest sampled free block is 4,608 B.
The original FAIL remains in the report; a separate two-minute repeat after
repositioning investigates the same stream without overwriting it.

That separate **120-second HE-AAC 64 kbit/s HTTPS repeat passed**, including
idle recovery and saved-setting restoration. It retained full 44.1 kHz stereo
PCM and recorded 645 status responses, maximum HTTP latency 329 ms and p95
109 ms. The acceptance window reports mean whole-radio CPU 63.462%, peak
65.7%, minimum free heap 16,784 B and largest free block 6,912 B. No runtime
allocation/decoder/TLS fault or reset was captured during playback. Restoration
performs its documented software reboot. Minimum decoder stack
margin was 4,032 B. RSSI ranged from −77 to −58 dBm during actual playback.
This repeat does not establish the cause of the earlier failure or qualify
an arbitrary duration/stream. Both results remain separately recorded.

The three 40-second controlled load cases also pass after repositioning, with
the same image and acceptance thresholds. Their diagnostic 5..35 s windows are:

| Profile | Decoder CPU | Whole-radio CPU | Minimum free heap | Largest free block |
| --- | ---: | ---: | ---: | ---: |
| LC 48 kHz stereo | 19.217% | 47.167% | 76,668 B | 63,488 B |
| HE 48 kHz stereo | 38.183% | 61.700% | 42,804 B | 32,768 B |
| HEv2 44.1 kHz stereo | 42.567% | 66.367% | 43,104 B | 32,768 B |

Restoration passes, no allocation/decoder fault was captured, and minimum
decoder stack margin is 2,824 B. These are later runs with changed RF conditions,
not an isolated attribution of every difference to the new memory layout.

## HTTP matrix and remaining memory investigation

The later HTTP matrix passes AAC-LC 128, HE-AAC 64, HE-AACv2 16 and MP3
256 kbit/s. HE-AAC 32 kbit/s fails the existing largest-free-block trend gate.
Its first three steady-window largest blocks are 19,456 / 15,872 / 14,336 B;
the last three are 9,216 / 14,336 / 10,752 B. Their medians decrease by
5,120 B, exceeding the 4,096 B allowance. Playback continued, but that is not
a PASS under the existing combined acceptance criteria.

There are no captured allocation/decoder/TLS/panic errors in this HTTP matrix.
Idle free heap changes from 145,968 B to 146,004 B, with a 114,688 B largest
block before and after. Recovery and saved-state restoration pass. This bounds
the observation; it does not identify the transient allocation causing fragmentation.

The next investigation is a longer HE-AAC 32 HTTP / 64 HTTPS observation with
bounded network-allocation or coherent heap/TCP counters. The current codec
allocation trace explicitly excludes network and TLS allocations. Inspection
of the pinned ESP-IDF source confirms that its heap-backed lwIP allocator still
enforces the configured **16 TCP PCB** limit and can reclaim old TIME_WAIT
connections. An unbounded TCP-PCB list is therefore not an established cause.
The checked source hashes/configuration and this finding are retained in
`network-allocation-audit.json`. Keep the current failure thresholds until the
cause and longer-term behavior are measured.

## Other codecs and finite files

All **18 local playback/EOF cases** pass, plus restoring the saved station.
They cover automatic and explicit codec selection for MP3 320 kbit/s, FLAC
level 8, Vorbis q10, Opus 510 kbit/s, AAC-LC 320 kbit/s, AAC-LC 22.05 kHz mono,
HE-AAC 44.1 and 48 kHz stereo, and HE-AACv2 44.1 kHz stereo. No allocation,
decoder or panic fault is captured. Minimum decoder stack margin is 2,732 B.
These finite-file checks validate reported full PCM format and completion;
they are not an acoustic measurement or a long-duration test of every codec.

## OTA completion and saved evidence

Three additional OTA transfers passed: app0 to app1 in 20.860 s, back to app0
in 21.125 s, and to app1 during playback in 20.734 s. Together with the initial
transition this makes four successful transfers. Running-image hashes, Wi-Fi,
settings and playlist equality pass; serial health and restoration pass.
The final snapshot confirms the candidate hash in app1 and resumed saved-station
playback. Deep sleep remains disabled in this test image.

The [retained evidence](../tests/results/esp32c3-aac-asymmetric-production-20261004/)
contains every attempted baseline/candidate/public/local/OTA run, both sides of
the board repositioning, raw CPU/status records, QEMU PCM and pointer results,
matching physical/QEMU native-patch audits, and exact source snapshots. It also
preserves both versions of the host runner used before/after adding sanitized
exception diagnostics. `implementation.json` hashes the records.

Run `python tests/test-aac-asymmetric-production.py`. Its ten checks recompute
the full PCM equality, actual load summaries, both failed public memory gates,
the successful relocated HTTPS window and firmware/OTA fingerprints. A passing
evidence check does not change any original hardware FAIL into PASS. The build
option stays experimental while fragmentation and longer-duration acceptance
remain unresolved.

## Reproduce

For QEMU, use the preceding pointer-audit configuration plus the production
asymmetric defaults. Disable both `CONFIG_YORADIO_QEMU_AAC_LOW_WORKSPACE` and
`CONFIG_YORADIO_QEMU_AAC_ASYMMETRIC_OWNER`, and run
`tools/codec_benchmark/run_aac_asymmetric_owner.py --production-path` with the
previous low-QMF baseline result and synthetic WAV. Pass `--input` for each
of the five complete retained recordings.

Physical tests use the existing runners from [firmware testing](ESP32C3_TESTING.md):
three `diagnostic.py run --suite load` AAC cases, `diagnostic.py ota_transition`,
the public stream matrix with a 60-second observation and 0.1-second request
interval, and the finite all-codec and OTA suites. Each image must have its
exact adjacent `sdkconfig`. Only one board-controlling runner runs at a time.

Results below and the saved evidence distinguish decoder equality, bounded
physical checks and outstanding acceptance gates. A successful firmware build
or evidence-validation test alone cannot promote this configuration.
