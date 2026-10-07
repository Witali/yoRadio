# FLAC source depth and signed-16 output

## Problem and change

The native C3 adapter previously accepted only 8/16-bit FLAC. The shared core
rejected depths above 16, left 12-bit samples unscaled, and added an unsigned
8-bit bias while still returning `short` elements. The native output service
then interpreted those shorts as packed bytes. This could change both amplitude
and timing for an otherwise valid 8-bit stream.

The decoder now accepts **4 through 24 source bits** and always returns
**signed 16-bit PCM**. Lower depths are scaled up; higher depths discard their
least significant bits by arithmetic right shift, matching FFmpeg's undithered
s16 conversion. Decoding and stereo reconstruction retain their original
integer precision until that final output conversion. This is a 16-bit output
device; it is not a claim of retaining 24 output bits.

Source depth remains available through `FLACGetBitsPerSample` and the native
stream metadata. `FLACGetOutputBitsPerSample` and the adapter's named
`pcm_bits_per_sample` describe the callback buffer. C3 queue sizing and audio
duration use the latter. The Arduino consumer also uses the actual output
representation and accepts the extended source range in both FLAC headers.

LPC reconstruction adds the residual in 64 bits, checks its representability,
and validates subframe/decorrelated sample ranges before output. Invalid depth
errors are negative, so they cannot be mistaken for a successful decoder state.

## Standards and limits

[RFC 9639](https://www.rfc-editor.org/rfc/rfc9639.html#section-9.1.4)
defines source depth separately from a player's output format. Its
[subframe depth rules](https://www.rfc-editor.org/rfc/rfc9639.html#section-9.2.3)
require one extra bit for a stereo side channel. Therefore 24-bit stereo tests
include 25-bit side values. The [prediction arithmetic guidance](https://www.rfc-editor.org/rfc/rfc9639.html#appendix-A.3)
also requires a wider accumulator than the stored PCM sample.

This change does not finish FLAC conformance: depths above 24, more than two
channels, blocks above 8192, native Ogg FLAC mapping, frame CRC validation,
mid-stream channel/rate changes and broader rates/containers remain separate work. The C3 output currently accepts
source rates from 8 to 48 kHz. Host tests do not qualify Arduino boards physically.

## Host evidence

The tests compile the actual shared core in both C3 segmented/512-frame and
Arduino contiguous/2048-frame modes, plus the actual C3 streaming adapter with
irregular input chunks. ASan, UBSan and leak detection are enabled.

| Fixtures | Count | Coverage | PCM result in all three paths |
| --- | ---: | --- | --- |
| Deterministic small frames | 120 | 4/8/12/16/20/24 bits; mono, independent stereo, left-side, right-side, mid-side; constant, verbatim, fixed order 4, LPC order 32 | Exact |
| Large frames and short tail | 10 | 24 bits, blocks of 8192, same five channel modes, verbatim/LPC32 | Exact |
| FFmpeg encoded stress files | 4 | 64 seconds, full-precision 24-bit noise/tones, four stereo modes | Exact |
| FFmpeg encoded large blocks | 4 | 12 seconds, 24 bits, blocks of 8192, four stereo modes | Exact |
| Physical-test tone fixtures | 4 | 12 seconds, 8/12/20/24 bits, stereo LPC32 | Exact |

**142 fixtures / 426 decoder comparisons** match both FFmpeg s16 output and
the known source PCM. The old-code baseline retains 12 failures out of 15
comparisons: 8/12-bit output is wrong or rejected, 20/24-bit input is rejected,
and the 16-bit control passes. No old failures are discarded.

Three large fixtures additionally exercise **46 persistent allocation failures
and 46 subsequent successful reopens** in the actual adapter/core. Each run
releases every tracked C allocation; recovered PCM matches the successful
baseline. The allocator wrapper covers their malloc/realloc/free calls, not
every C++ runtime allocation. Peak tracked storage in the largest host case is
118,528 bytes; this is not a board free-heap measurement.

The previous 16-bit truncation regression still passes all 16 file cases in
each storage mode with identical FFmpeg PCM. Edge checks add 25-bit constant
side samples and corrupt LPC overflow. Callback tests verify that 8/24-bit
metadata cannot alter the signed-16 queue layout or audio duration.

## Firmware and hardware qualification

The testing image is `firmware/development/esp32c3-flac-depths/app.bin`, with its
exact `sdkconfig` beside it. No deep sleep, DIO 80 MHz, full-rate PC19 AAC, and
the experimental whole-block DMA output are retained.

| Section | Before | After |
| --- | ---: | ---: |
| IRAM text | 43,354 B | 43,354 B |
| DRAM data | 12,620 B | 12,620 B |
| DRAM BSS | 29,464 B | 29,464 B |
| RTC data | 2,688 B | 2,688 B |
| Application image | 1,576,208 B | 1,576,432 B |

No new PCM/workspace allocation is introduced. Native WebUI OTA passed, including
preservation of Wi-Fi configuration, playlist and settings. This image has been
tested on the board, but **fails hardware qualification**:

- A subsequent 60-second 16-bit/48 kHz stereo control under frequent WebUI
  requests passes CPU, playback and settled heap recovery: mean CPU 69.43%,
  peak 70.3%, minimum heap 69,184 B, largest block at least 55,296 B, maximum
  HTTP response 125 ms, audio/wall ratio 1.00154. Its serial runtime check also
  passes. This control does not qualify the failing high-depth cases below.

- The 16 depth/stereo playback cases (AUTO and explicit FLAC) include 12 status/
  EOF passes and four WebUI timeouts on 24-bit left/right-side, 8192-sample blocks.
  The four following natural-EOF state checks also fail; their observation begins
  before the delayed playback has ended. All 16 settled EOF heap checks and all
  16 Stop heap checks pass. These memory checks do not override playback failures.
- The serial runtime gate fails. Large-block streams produce real allocation
  failures, including 1700-byte network allocations with largest free blocks
  below 1700 bytes. RSSI around the timeouts is approximately -64/-65 dBm.
- The synthetic 20/24-bit LPC32 tones saturate the CPU and deliver less than one
  second of audio per wall-clock second. Register dumps recur at five-second
  intervals; most decoded PCs are in `restoreLinearPrediction`. The SDK marks
  `MCAUSE=0xdeadc0de` as a software diagnostic dump without a useful trap cause.
  There is no recorded reboot during playback. The capture did not retain the
  watchdog heading, so the register dump alone does not prove a particular reset
  cause. It remains a failed runtime check.

The tone fixture deliberately has one nonzero coefficient in an order-32 LPC
predictor. It exercises a legal expensive code path, but does not represent all
real order-32 predictors. Further optimization must also test dense coefficients,
segment boundaries and exact PCM, rather than only this sparse fixture.

Retained evidence: `tests/results/esp32c3-flac-depths-20261005/`, including original
failed reports and compressed serial/status observations. Next work is to reduce
predictor overhead and encoded-frame/workspace memory pressure, then repeat the
failed cases and sustained CPU checks without relaxing acceptance gates.

## Reproduction

```text
python tools/codec_benchmark/run_flac_depths.py --output NEW_HOST_DIRECTORY
python tools/audio_test_server/generate_flac_depths.py --large-blocks --output NEW_LARGE_FIXTURES
python tools/codec_benchmark/run_flac_depths.py --fixtures NEW_LARGE_FIXTURES --allocation-failures --output NEW_OOM_DIRECTORY
python tools/audio_test_server/generate_flac_high_depth.py --seconds 64 --output NEW_STRESS_FIXTURES
python tools/codec_benchmark/run_flac_depths.py --fixtures NEW_STRESS_FIXTURES --output NEW_STRESS_RESULT
python tools/codec_benchmark/run_flac_bounds.py --output NEW_BOUNDS_DIRECTORY
```

Use `--revision c023564c --fixtures FIXTURE_DIRECTORY --case FIXTURE_NAME` to
retain the old-code failure without changing the checkout. Use new output
directories. The generators and HTTP server are board independent; they can
also supply CYD and ESP8266 tests.
