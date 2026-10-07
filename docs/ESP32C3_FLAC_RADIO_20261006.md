# Real-radio FLAC predictor study — 2026-10-06

## Question and scope

How often does an encoder choose order-32 linear prediction on actual radio
audio, and how much work does this impose on the ESP32-C3 compared with a
maximum order of 12?

The corpus contains ten 120-second music recordings from ten distinct
[SomaFM channels](https://somafm.com/listen/). This is a deliberately varied
music sample from **one broadcaster**, not a random survey of radio stations,
speech, recording masters or existing FLAC collections. Captured AAC and music
PCM/FLAC stay in the ignored local workspace; Git retains measurements,
public source URLs, commands, hashes and test sources.

The comparison disables **high-order LPC above 12** in the control. It does
not disable all prediction: the control still uses ordinary LPC up to order 12.
Both sides encode identical PCM losslessly. No decoder precision, feature or
firmware change was made for this study.

## Encoding and exactness

- Capture from official HTTPS playlists, with certificate verification enabled.
  All ten observed sources were HE-AAC, 44,100 Hz, stereo. Keep native rate and
  channels; decode each excerpt to a common **24-bit** PCM WAV.
- Encode twice with FFmpeg 8.1.1, `-compression_level 12`, differing only in
  `-max_prediction_order 32` versus `12`. LPC32 is **allowed, not forced**.
  Level 12 is FFmpeg's highest numbered preset; no claim is made that it is the
  smallest possible file under every custom encoder setting.
- This is a demanding 24-bit FLAC scenario. Converting lossy AAC to 24-bit PCM
  does not recover information lost in the broadcast encoder. These results
  do not directly measure ordinary 16-bit CD FLAC.
- Compare both FLAC files against the common source at full 24-bit precision,
  then check the firmware's 16-bit output against FFmpeg. All round trips match.
- Decode all 20 complete files through the unmodified segmented FLAC core,
  contiguous Arduino core and ESP32-C3 streaming adapter under ASan/UBSan:
  **60/60 exact PCM comparisons pass**. Separately, all 20 instrumented host
  decodes pass the same PCM comparison.

The observation build adds two host-only log hooks to a copy of the production
core. It records subframe type, block length, order, effective/nonzero taps,
coefficient precision and eligibility for the existing recurrence optimization.
It does not instrument the firmware used for timing. The parser is the actual
production parser; FFmpeg provides the independent PCM reference.

Order percentages are weighted by **channel-samples**, including the shorter
last block, not by a simple count of frames. A stereo frame contains two
channel subframes; the reported percentage is not the fraction of stereo
frames where either channel uses LPC32. Every file covers 5,292,000 stereo
sample frames / 10,584,000 channel-samples. Order analysis covers the full
120 seconds, while the physical measurements below cover a shorter prefix.

## Predictor frequency and compression

| Channel | Genre | LPC32 share with max 32 | Mean order, max 32 | Mean order, max 12 |
| --- | --- | ---: | ---: | ---: |
| Groove Salad | Ambient / downtempo | 13.28% | 27.35 | 11.99 |
| Drone Zone | Ambient / drone | 7.48% | 24.06 | 11.33 |
| Indie Pop Rocks! | Indie pop / rock | 8.05% | 25.51 | 12.00 |
| Sonic Universe | Jazz | 65.80% | 31.14 | 11.15 |
| Boot Liquor | Americana / country | 55.51% | 30.29 | 11.53 |
| Seven Inch Soul | Soul | 40.55% | 29.29 | 11.63 |
| Folk Forward | Folk | 75.10% | 31.20 | 11.23 |
| Illinois Street Lounge | Lounge / vintage | 11.93% | 26.98 | 11.99 |
| The Trip | House / trance | 6.77% | 24.96 | 11.98 |
| Bossa Beyond | Bossa / samba | 73.44% | 31.36 | 11.21 |
| **Combined** | | **35.79%** | **28.21** | **11.61** |

With max 32, **99.19%** of channel-samples use orders above 12. The mean
number of nonzero coefficients is 28.20 (versus 11.61 with max 12). No observed
subframe in either variant qualifies for the special repeated/alternating
coefficient recurrence. Thus the arbitrary-coefficient path matters for real
audio when this encoder is explicitly allowed to choose high orders.

Total FLAC size is **216,130,617 B** with max 32 versus **224,323,842 B** with
max 12: **8,193,225 B / 3.65% smaller**. This is the byte-weighted reduction
of the complete corpus, not an unweighted average of percentages.

This does not establish that LPC32 is common in existing FLAC files. The
[Xiph encoder presets](https://www.xiph.org/flac/documentation_tools_flac.html)
use lower maximum orders, and the
[FLAC streamable subset at rates up to 48 kHz](https://www.rfc-editor.org/rfc/rfc9639.html#section-7)
limits LPC order to 12. Full FLAC permits 32. The
[FFmpeg encoder preset implementation](https://www.ffmpeg.org/doxygen/8.1/libavcodec_2flacenc_8c_source.html)
is the reference for this study's chosen settings.

## Physical measurement method

The existing `esp32c3-flac-dispatch` development image was used without flashing:
ESP32-C3 at 160 MHz, DIO 80 MHz flash, no deep sleep, Wi-Fi code in flash,
experimental whole-block DMA output with three-block startup prefill.

- App SHA-256: `eaf4c54ad57f7fc30d7b3d59ee33b560dd3d6e723b1d1fb887264f194104d28e`.
- ELF SHA-256: `4d82535ef2c88884f3f2a71544396dfef9115169929427e7fa69a36204b2b859`.
- SDK configuration SHA-256: `c9abe45e85e5f11911ac21db6da448db231a3761288eda7de6e9900ed9eb32a2`.

Channel RSSI minima during the main series ranged from -73 to -64 dBm.
These values describe reception conditions; they do not prove or exclude a
network cause for an individual pause.

Each file plays for 115 seconds with a five-second guard before EOF. The first
ten seconds are discarded for steady-state statistics. Pair order alternates
32/12 then 12/32 across channels. This is one run per variant, not a confidence
interval over repeated independent sessions.

Files are served over LAN HTTP with normal TCP backpressure and no artificial
average-bitrate pacing. Variable-rate FLAC can require bursts; pacing a file
solely by its average bitrate can create unrelated input starvation. WebUI
status is polled with a 0.1-second delay between requests. This is load testing,
not an estimate of CPU consumption with the browser closed.

Three different measurements must stay separate:

1. **Total CPU busy:** FreeRTOS runtime accounting, `100 - idle`, including
   networking, output and the test's WebUI activity.
2. **Decoder task CPU:** runtime share of `audio_decode`; includes wrapper and
   task work, not an isolated measurement of the LPC dot product.
3. **Elapsed FLAC call time:** time inside the decoder call per second of
   decoded audio. Includes preemption; it is not CPU cycle utilization.

CPU means are weighted by complete profiling-window durations, approximately
five seconds each. Only windows wholly inside the measurement period count.
Firmware timestamps determine their duration; host timestamps locate the
window in its test. **Fully busy** means at least **99.9%** at the profiler's
0.1% resolution. Short peaks inside these windows are not resolved. Coverage,
malformed logs and delayed/missing-log warnings are retained explicitly.
Intervals spanning a log gap of at least ten seconds are excluded: the last
reported percentage cannot safely be attributed to the whole missing interval.

The `audio_decode` task name matches the profiler's decoder category. Other
named subfields are retained verbatim but are not a complete task breakdown:
for example, this image's matching does not recognize the observed `tcpip`
task name, so its printed `tcpip=0.0%` is not evidence of zero TCP/IP work.
Total busy time is calculated independently from idle and is unaffected by
that category-name mismatch.

Original acceptance gates are preserved: CPU peak at most 85%, WebUI request
under 2 seconds, heap budgets and decoder progress. The existing progress gate
allows audio/wall from 0.9 to 1.1; therefore **PASS alone does not establish
gap-free playback**. The report separately lists the actual audio/wall ratio
and any shortfall. No output recording or DMA underrun counter is available
in these measurements, and natural EOF is not being retested here.

## Physical results

| Metric | Maximum LPC12 | Maximum LPC32 |
| --- | ---: | ---: |
| Mean total CPU | 76.04% | 80.57% |
| Peak total CPU (complete retained windows) | 83.1% | 87.2% |
| Mean decoder-task CPU | 25.53% | 34.53% |
| Elapsed decoder time per second of audio | 266.2 ms | 392.3 ms |
| Decoded audio / wall time | 0.99467 | 0.92169 |
| Observed time at CPU >=99.9% | 0.00% | 0.00% |
| Observed time at CPU >=85% | 0.00% | 9.73% |
| Usable CPU window duration | 1007.951 s | 994.593 s |
| CPU coverage of the measurement period | 95.91% | 94.64% |
| Original load gates: PASS / FAIL | 10 / 0 | 5 / 5 |

Allowing order 32 increases mean total CPU by **4.54 percentage points** and elapsed decoder cost per second of audio by **47.4%**. The CPU difference alone understates the problem because several high-order runs produce less audio per wall-clock second. No >=99.9% CPU interval was observed; that statement applies to the retained intervals, not to unobserved gaps or instantaneous peaks.

### Per-channel paired measurements

Entries separated by a slash are **max 12 / max 32**, in that order. A ratio of 1 means one second of audio produced per wall-clock second. Size reduction is relative to the max-12 file.

| Channel | CPU mean, % | CPU peak, % | Decode, ms/audio-s | Audio/wall | Size reduction | Original gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Groove Salad | 75.17 / 78.92 | 77.1 / 81.3 | 273.4 / 386.5 | 1.0005 / 0.9378 | 6.85% | PASS / PASS |
| Drone Zone | 70.07 / 75.35 | 71.6 / 76.9 | 253.5 / 363.0 | 1.0016 / 0.9862 | 4.68% | PASS / PASS |
| Indie Pop Rocks! | 78.39 / 81.05 | 79.6 / 82.3 | 271.8 / 374.5 | 0.9963 / 0.9296 | 6.57% | PASS / FAIL |
| Sonic Universe | 74.67 / 78.77 | 77.2 / 84.1 | 261.4 / 414.0 | 1.0006 / 0.8848 | 1.11% | PASS / FAIL |
| Boot Liquor | 74.52 / 81.07 | 79.3 / 83.7 | 269.1 / 407.2 | 0.9582 / 0.8901 | 1.12% | PASS / FAIL |
| Seven Inch Soul | 78.25 / 83.03 | 80.1 / 83.9 | 266.4 / 401.9 | 0.9962 / 0.9078 | 1.59% | PASS / PASS |
| Folk Forward | 77.88 / 83.00 | 83.1 / 86.7 | 269.8 / 413.2 | 0.9963 / 0.9021 | 0.81% | PASS / FAIL |
| Illinois Street Lounge | 76.61 / 80.13 | 78.4 / 81.6 | 267.8 / 387.7 | 0.9984 / 0.9252 | 7.28% | PASS / PASS |
| The Trip | 75.22 / 78.88 | 77.8 / 81.8 | 267.1 / 366.5 | 1.0002 / 0.9503 | 6.37% | PASS / PASS |
| Bossa Beyond | 79.83 / 85.61 | 81.4 / 87.2 | 262.4 / 414.1 | 0.9985 / 0.9031 | 1.19% | PASS / FAIL |

### Failed gates and coverage

- **Indie Pop Rocks!, max 32:** Progressive heap loss during continuous playback. Maximum HTTP 500 ms; audio/wall 0.92961.
- **Sonic Universe, max 32:** WebUI response exceeded 2 s. Maximum HTTP 2156 ms; audio/wall 0.88484.
- **Boot Liquor, max 32:** Decoded audio is not progressing in real time. Maximum HTTP 1359 ms; audio/wall 0.89014.
- **Folk Forward, max 32:** CPU budget exceeded. Maximum HTTP 172 ms; audio/wall 0.90210.
- **Bossa Beyond, max 32:** CPU budget exceeded. Maximum HTTP 172 ms; audio/wall 0.90309.

An original gate reports the first failed condition. Later conditions may not have run, so the numeric diagnostics and separate runtime check must also be read. The original suite includes edge CPU samples; the table uses only complete windows, so its extrema can differ slightly.
CPU log gaps in **Indie Pop Rocks!, max 12**: 10.281 seconds excluded. Remaining complete-window coverage: 87.21%.

All 20 separate filtered-log runtime checks pass: no captured decoder/allocation error, panic or unexpected reboot during the load periods. This does not override the load-gate failures or establish acoustic continuity. No per-case Stop heap-recovery test was included in the main series; the follow-up below adds that check for selected pairs.

### Selected repeat with Stop recovery

Both selected pairs were repeated in the reverse order (12 then 32), with
12-second settled heap observations before and after each 115-second load.
These repeats are reported separately and are not pooled into the main means.

| Channel / maximum order | CPU mean / peak | Decode, ms/audio-s | Audio/wall | Load / Stop recovery |
| --- | ---: | ---: | ---: | --- |
| groovesalad / 12 | 74.96% / 77.1% | 270.1 | 0.99982 | PASS / PASS |
| groovesalad / 32 | 78.53% / 79.8% | 383.9 | 0.93891 | PASS / PASS |
| indiepop / 12 | 78.60% / 80.0% | 271.3 | 0.99523 | PASS / PASS |
| indiepop / 32 | 81.55% / 83.6% | 381.4 | 0.92686 | PASS / PASS |

All four repeated load gates, four initial heap checks, four Stop-recovery
checks and the final restore check pass. The initial Indie Pop Rocks! LPC32
heap-gate failure remains a failure in the main series. It did not recur
here, and Stop recovery passed; this is insufficient evidence of a
persistent decoder leak. The approximately 6-7% audio shortfall in the
two high-order recordings **does recur**, despite idle CPU time.

### Interpretation of CPU headroom

A mean CPU value below 100% does not establish that every output deadline is
met. The present pipeline runs the decoder above the output task (priorities
7 and 6). Four 512-frame DMA descriptors at the fixed 48 kHz output rate hold
at most 42.67 ms in total; the amount already filled and safe to play when a
new decode starts can be smaller. A long uninterrupted decoder burst can
therefore be important even when there is idle time elsewhere in the window.
Observed per-file maximum FLAC calls were 48.4-54.5 ms with max 32 versus
33.6-40.3 ms with max 12.
This is a plausible scheduling/buffering explanation to investigate, not a
measured underrun diagnosis. Network/input waits and output preparation also
need separate timing before attributing the entire shortfall to one cause.

Next experiment: measure input-wait time, PCM queue waits, maximum contiguous
decode work and DMA underruns together. Then compare bounded decoder yields
or output scheduling on these identical recordings, retaining exact PCM and
all current CPU/heap gates. Do not remove supported FLAC orders to hide the
slow path.

## Reproduction and retained evidence

Use Python, FFmpeg/ffprobe, and the existing WSL g++ sanitizer toolchain for host
checks. Board measurements need the matching awake profiling image, its native
USB serial port, and a LAN address reachable from the ESP32-C3. The capture,
encoding and fixture server are board-independent; physical status/profiling
checks here use the C3 API and log format.

Use fresh output directories. Live broadcasts cannot be downloaded again with
identical content: exact replay requires the retained local recordings whose
hashes are in the manifest. A new capture is a new corpus, not a reproduction
of the same audio samples.

```text
python tools/codec_benchmark/capture_radio_flac.py --output .build/NEW_RADIO/recordings --seconds 120 --jobs 5
python tools/codec_benchmark/analyze_radio_flac.py --fixtures .build/NEW_RADIO/recordings --output .build/NEW_RADIO/analysis
python tools/codec_benchmark/run_flac_depths.py --fixtures .build/NEW_RADIO/recordings --output .build/NEW_RADIO/host-pcm
python tools/esp32c3_tests/radio_flac_study.py --board http://BOARD_IP --host HOST_IP --serial-port COM_PORT --firmware firmware/development/esp32c3-flac-dispatch/app.bin --fixtures .build/NEW_RADIO/recordings/manifest.json --seconds 115 --output .build/NEW_RADIO/board
python tools/esp32c3_tests/summarize_radio_flac.py --board-results .build/NEW_RADIO/board --manifest .build/NEW_RADIO/recordings/manifest.json --analysis .build/NEW_RADIO/analysis/report.json --output .build/NEW_RADIO/summary.json
python tests/test-radio-flac-study.py
python tests/test-radio-flac-evidence.py
```

The board runner stops between cases and restores the saved station at the
end. It does not flash an image. Keep every original failure when repeating
a case; a later successful run must not replace the first observation.

To retain a completed study using this exact development image, run the
following with a fresh evidence destination. The saver verifies the local
recording hashes, source identities and firmware configuration, and refuses
to save a board run before its final restore outcome is recorded.

```text
python tools/codec_benchmark/save_radio_flac_evidence.py --work .build/NEW_RADIO --output tests/results/NEW_RADIO_EVIDENCE
```

Add `--extra-board PATH_TO_REPEAT` to keep a separate repeat alongside the
original outcomes. The original broadcast media are deliberately omitted.

The [retained evidence](../tests/results/esp32c3-radio-flac-20261006/manifest.json)
contains compressed raw diagnostic/status/order logs, complete reports, source
snapshots and integrity hashes. Local source audio is in
`.build/radio-flac-20261006/recordings/`. The firmware remains **not production
qualified**; this study does not resolve the earlier large-block allocation,
artificial dense-LPC32 saturation or long HE-AACv2 heap issues described in the
[predictor report](ESP32C3_FLAC_PREDICTOR_20261006.md).
