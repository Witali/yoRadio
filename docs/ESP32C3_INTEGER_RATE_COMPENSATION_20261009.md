# Integer PDM rate compensation: rejected linear candidate

## Result

The experiment removes the **nominal sample-count drift in software**, but
its linear interpolator does not meet the output-quality requirement for
48 kHz sources. It is **disabled by default and not installed on the board**.
No physical CPU, timing, RAM, analog-noise or continuity pass is claimed.

The [latest physical run](ESP32C3_INTEGER_QUALIFICATION_20261009.md) records
11 late DMA events with input/PCM waits. The common resampler targets 48,000
frames/s while the integer PDM clock nominally consumes 625000/13 frames/s.
That mismatch consumes an extra 0.962 s of buffered audio in ten minutes.
It is a plausible cause of late starvation, not proof that every DMA event
has this cause. Firmware defaults and the board's installed image stay unchanged.

## Implemented experiment

`CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION` selects the exact rational
phase period 625000 and input step `source_rate * 13`. It preserves the
integer PDM divider, codec calculations, rate/channel metadata, existing
PCM buffer and linear interpolation. A Q32 reciprocal avoids division in
fraction calculation. The default-off path keeps the prior Q16 reciprocal
and 48 kHz bypass. Compensation necessarily removes that bypass.

The option excludes fractional-clock and direct-DMA modes. The audited,
build-local driver validates the 160 MHz source, integer divider 2, BCLK
divider 13, PCM rate 48 kHz and FP/FS 960/480. Unknown driver sources fail
configuration. The SDK checkout itself is not modified.

[Espressif's I2S guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/peripherals/i2s.html#pdm-tx-mode-in-pcm-format-with-pcm-to-pdm-converter)
describes PCM-to-PDM upsampling configuration. The experiment preserves that
configuration; it changes application resampling only. Nominal clock ratios
do not constitute measurement of the physical crystal frequency.

## Executed tests

The actual staged-output C implementation, with guarded SDK/DMA stubs, passes
35 AddressSanitizer/UBSan cases: nine standard source rates, short/tail cases,
all rational phases through a legal odd rate, distinct stereo pseudo-random
PCM, five sine tones and ten-minute sample counts at 44.1/48 kHz. Independent
64-bit rational linear interpolation is the numerical reference. No tested
sample differs by more than 2 LSB from that reference (the tones differ by
at most 1 LSB). This is separate from the AAC decoder's 3-LSB tolerance.

Both ten-minute source inputs produce exactly **28,846,153 frames**, matching
the independent finite-sequence formula `1 + floor((N-1)*625000/(13*Fs))`.
The fake driver consumes immediately; this is not a physical DMA test.

### Why the linear version is rejected

Two-second 48 kHz, 20,000-peak-PCM sine inputs are compared with the ideal
continuous sine at the output's rational sampling times. Gain is total RMS,
including interpolation distortion, not a separated fundamental measurement.

| Tone | Output RMS gain | Error RMS relative to ideal sine |
| ---: | ---: | ---: |
| 100 Hz | -0.00013 dB | -90.31 dB |
| 1 kHz | -0.0123 dB | -56.16 dB |
| 10 kHz | -1.233 dB | -16.44 dB |
| 18 kHz | -3.659 dB | -6.96 dB |
| 20 kHz | -4.229 dB | -5.39 dB |

The small coefficient rounding error does not remove the much larger
frequency-response error. Existing 48 kHz playback bypasses interpolation;
introducing this loss would be a regression. Therefore do not deploy this
candidate merely to obtain better DMA counters.

The unchanged default mode separately passes staged/direct/profile output
regression: all four paths produce identical 12,331,776-byte PCM streams,
SHA-256 `5c0536fec9f7e968a8de7e92f868f86032b11c4b4f4ba3304b82804b8f1f0f09`.
Normalizer regression covers 648 cases with zero error. Five PDM clock tests
verify readback math, rejection of unknown sources and retained integer setup.

## Next implementation candidate: finite impulse response interpolation

An offline analytical study evaluates a Blackman-windowed sinc kernel across
all 625 rational phases for 48 kHz input. A 256-phase table plus endpoint uses
Q19 coefficients, exact DC normalization and interpolation between adjacent
phase-table convolution results. These are **calculated candidates**, not
implemented firmware or measured CPU costs.

| Taps | Coefficient table in Flash | Stereo history RAM, excluding state | Worst phase gain at 20 kHz | Coefficient approximation bound, PCM LSB |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 16,448 B | 64 B | -1.3768 dB | 0.837 |
| 24 | 24,672 B | 96 B | -0.1894 dB | 0.873 |
| 32 | 32,896 B | 128 B | -0.00629 dB | 1.126 |

The bound compares stored/interpolated coefficients with the corresponding
exact finite kernel for any full-scale input vector. It excludes kernel
approximation, final accumulator rounding, clipping and analog output. It
is not a decoder-quality result. The 32-tap candidate requires about 6.154
million tap multiply-accumulates/s for two convolutions per stereo output
frame; actual RV32 time and accumulator code must be measured before adoption.

Next: implement only the promising high-quality candidate in an isolated
experiment; verify startup latency, EOF draining, Stop/generation reset,
rate changes, intersample overshoot/saturation and full-scale stereo. Retain
reference PCM and compare hot-loop cost on C3 before a matched ten-minute
real-time AAC/FLAC test. Do not reduce AAC features, sample rates or its
precision requirement to pay for resampling. A lower-CPU implementation or
the separately qualified fractional-clock path may be preferable.

## Reproduction

```powershell
python tools/codec_benchmark/run_integer_rate_host.py --output NEW_DIRECTORY
python tools/codec_benchmark/run_output_dma_host.py --profile --output ANOTHER_DIRECTORY
python tools/codec_benchmark/compare_integer_rate_filters.py --output NEW_JSON
python tests/test-pdm-clock.py
```

The C tools use local WSL GCC on Windows, with address/undefined-behavior
sanitizers. [Saved sources and results](../tests/results/esp32c3-integer-rate-20261009/README.md)
retain hashes, logs and limitations. The initial generated-unit filename
collision was fixed before the successful host run; it was a test-generator
compile failure, not a board or codec failure.
