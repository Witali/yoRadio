# ESP8266 AAC-LC flash-source benchmark, 2026-09-08

## Result

All three low/moderate-rate AAC cases FAILED physical continuity at
44.1 kHz: the output substituted neutral PDM while no ready PCM was
available, despite Wi-Fi being disabled and the source being in flash.
Decode-only is faster than realtime, but the complete output path is not
continuous. No production decoder/output algorithms were changed by this test.

## Same methodology as MP3

Use the identical deterministic stereo 44.1-kHz/16-bit WAV from the
[MP3 benchmark](ESP8266_MP3_FLASH_BENCHMARK_2026-09-08.md): tones, chirp,
seeded noise, bursts and varying envelope, peak -3.01 dBFS.
Encode AAC-LC/ADTS at target 48/64/96 kbit/s, not high-bitrate AAC.
Actual ADTS-inclusive averages are 48.770 / 63.126 / 93.850 kbit/s.
Each file contains 45 frames including encoder priming/padding.

All three encoded files occupy 26,873 bytes in mapped internal flash.
No whole-file RAM copy or second input staging buffer: bounded reads go
directly to the decoder's existing input buffer. Decode complete files
in order and loop. Eight warmup frames followed by 1000 measured frames
give 23.219954 s PCM per case, 2000 PCM callbacks, about 22 clip loops.

Wemos D1 mini ESP8266EX, CPU160/QIO40, native Helix AAC-LC,
CONFIG_YORADIO_HELIX_AAC_SSO is OFF (same as ordinary production).
Mono output, AAC callback block 512 samples, standard I2S PDM32 GPIO3/RX,
2 x 512 DMA words, nominal 1.536 MHz / actual 1.538461 MHz carrier.
Normal 44.1-to-output-rate conversion retained. Runtime volume 128,
balance zero, normalization off; stored user settings are not changed.
Wi-Fi/HTTP/WebSocket services are disabled. No periodic UART printing
inside the measurement loop. RTOS interrupts/yields remain.

## Decoder only, no audio output

| Target AAC kbit/s | Decode time, 1000 frames | Average call | Maximum call | PCM time budget | Speed |
| --- | ---: | ---: | ---: | ---: | ---: |
| 48 | 15.039826 s | 15.039 ms | 16.334 ms | 64.77% | 1.543x |
| 64 | 15.614846 s | 15.614 ms | 16.968 ms | 67.25% | 1.487x |
| 96 | 16.138537 s | 16.138 ms | 17.510 ms | 69.50% | 1.438x |

All cases: nonzero mono PCM, 90,176 bytes free heap, task stack margin
1976 bytes. Elapsed decode-call time includes the PCM check and possible
preemption, excludes between-frame flash reads and RTOS yields. It is
not a direct whole-system CPU idle measurement.

For comparison on the identical source/rate, MP3-64 used 36.63% of its
PCM budget; MP3-128 42.32%; MP3-320 62.56%. Frame sizes differ, so use
normalized PCM budgets rather than comparing per-frame times alone.

## Decoder plus PDM and physical DMA

| Target AAC kbit/s | PCM | Wall time | DMA EOF | Underruns | Partial starts | FIFO empty | Result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 48 | 23.219954 s | 25.940231 s | 5076 | 2098 | 978 | 0 | FAIL |
| 64 | 23.219954 s | 26.929155 s | 5819 | 2841 | 978 | 0 | FAIL |
| 96 | 23.219954 s | 27.028452 s | 5894 | 2916 | 978 | 0 | FAIL |

Free heap: 85,164 bytes in all cases. Task stack margin:
1776 / 1776 / 1752 bytes. Actual decoder allocations: DRAM 6804,
IRAM 16,384 bytes. These are not the entire application's RAM usage;
Wi-Fi-off free heap must not be projected onto the live-radio build.
Fifty create/destroy cycles and fifty AAC selections returned heap to
the initial value in both variants, delta=0.

Physical wall time includes flash reads, scheduling, conversion and DMA
waits. Decoder-call timing in this mode includes synchronous waits in
the PCM callback: it is not decoder CPU cost and cannot be subtracted
from decode-only to obtain pure PDM CPU time.

Underruns are short neutral PDM retries, not a count of dropped AAC
frames or large audible pauses. DMA continued clocking; FIFO empty=0
does not mean continuous non-neutral audio. Counters are captured
before the final queued DMA payload necessarily drains.

## Conclusion and next diagnostic

- Lower compressed bitrate alone does not resolve the output stalls
  in the tested 48..96-kbit/s range at 44.1 kHz.
- Network starvation is excluded for this experiment. It can still
  independently affect live-radio playback.
- The decoder alone has average throughput headroom. A likely issue to
  investigate is the deadline for the next PCM block versus the amount
  of ready DMA data, including synchronous output waits and resampling.
  One DMA payload is about 10.667 ms, whereas an AAC decode-only call can
  reach 17.510 ms. This is a hypothesis about the cause, not a proven
  location of the stall or proof that more RAM alone will fix it.
- Next measure PCM callback gaps, ready DMA words, flash-read time and
  scheduling together; compare 44.1/48-kHz input with unchanged output
  settings before selecting a buffer or scheduling change.

Limitations: one deterministic clip and one measured capture per build;
no HE-AAC/SBR, no high-bitrate AAC, no analog capture/SNR/listening test,
no bit-perfect PCM comparison. Encoder padding and clip-loop boundaries
can produce quiet source sections; those are distinct from underruns.
Normal radio/WebUI acceptance remains unresolved.

## Saved evidence

- [Fixtures and regeneration](../tests/fixtures/aac_composite/README.md),
  [source and encoded hashes](../tests/fixtures/aac_composite/manifest.json).
- [Physical report](benchmarks/esp8266-aac-flash-2026-09-08/physical.json),
  [UART](benchmarks/esp8266-aac-flash-2026-09-08/physical.log).
- [Decode-only report](benchmarks/esp8266-aac-flash-2026-09-08/decode.json),
  [UART](benchmarks/esp8266-aac-flash-2026-09-08/decode.log).
- [Builds and binary hashes](benchmarks/esp8266-aac-flash-2026-09-08/builds.json).
- Diagnostic binaries/sdkconfig:
  firmware/development/esp8266-aac-flash-output/ and
  firmware/development/esp8266-aac-flash-decode/.

Repeat with the MP3 report's build settings, but set
YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX=OFF and
YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX=ON; keep FRAMES=1000.
Only toggle CODEC_RAM_AUDIO_OUTPUT for the comparison.
Capture at least 90 s physical / 65 s decode-only and require "complete".
The common summarize_mp3_matrix.cjs tool auto-detects AAC labels.
Physical reports deliberately return exit status 1 for these failed cases.
Restore ordinary production firmware after testing; do not leave the
Wi-Fi-disabled diagnostic build on the board.
