# ESP32-C3 codec performance checklist

This checklist tracks reproducible maximum-complexity tests for the native
ESP-IDF firmware on the single-core 160 MHz ESP32-C3 OLED board. Every codec is
fed the same deterministic 48 kHz stereo source from a dedicated flash
partition. No network reads occur while a codec is measured. The
source mixes independently seeded white/pink noise and two non-harmonic tones,
so lossless and perceptual encoders cannot benefit from a trivial silent input.

Build and flash the special non-OTA firmware, then generate the fixtures:

```powershell
.\tools\codec_benchmark\build.ps1 -IdfArguments '-p','COM9','flash'
.\tools\codec_benchmark\generate.ps1 -FfmpegPath C:\path\to\ffmpeg.exe
```

Run the automated flash and serial-log sequence:

```powershell
.\tools\codec_benchmark\run.ps1 -Port COM9
```

The benchmark layout has one `0x180000` factory application and uses every byte
between it and the unchanged SPIFFS partition as a `0x240000` `codec_test`
partition. The runner writes one fixture at a time at `0x190000`, resets the
board, and captures the automatically started local playback. A 16-byte header
before the encoded data identifies its codec and exact length. This layout has
no OTA slots. To keep the measurement isolated, the benchmark build does not
start Wi-Fi, WebUI, SPIFFS, OLED or button tasks. The normal firmware is not
affected by these compile-time exclusions.

`decode/audio` below is pure decoder CPU time divided by the duration of PCM it
produced. Values below 100% keep up in isolation; lower is better. The maximum
single call and uninterrupted playback must also pass.

## Result summary

| Codec fixture | Encoded limit | Baseline | Optimized | Stable |
| --- | ---: | ---: | ---: | :---: |
| MP3 | CBR 320 kbit/s | 26.3%, x3.79 | 26.1%, x3.82 | [x] |
| AAC-LC | CBR 320 kbit/s | 18.7%, x5.32 | 18.7%, x5.32 | [x] |
| FLAC | level 8, noise-heavy source | 13.5-13.7%, x7.28-7.39 | 13.4-13.7%, x7.28-7.45 | [x] |
| Ogg Vorbis | quality 10 | 36.4-36.9%, x2.70-2.74 | 36.3-36.8%, x2.71-2.74 | [x] |
| Ogg Opus | CBR 510 kbit/s, 20 ms frames | 42.2%, x2.36 | 42.1-42.2%, x2.36-2.37 | [x] |

The measured ratio covers the prebuilt Espressif decoder call itself. The
library's C3 archive is already compiled, so common pipeline changes are not
expected to materially change that number. Their benefit is outside the
decoder call: fewer task delays, state-lock operations, PCM copies and integer
operations. The optimized run retains 259396 bytes of free heap after the
larger PCM ring is allocated. All fixtures completed twice without decode
errors, restarts, watchdog reports or underruns.

## Common pipeline

- [x] Build the native component and firmware with `-O3`.
- [x] Measure decoder calls with `esp_timer_get_time()` in 5-second windows.
- [x] Report decoded audio duration, CPU time, real-time ratio, speed multiple,
      maximum call time and input/PCM byte counts.
- [x] Reduce unconditional one-tick delays without starving the idle task or
      triggering the task watchdog.
- [x] Avoid querying unchanged stream information for every decoded frame.
- [x] Reduce PCM packet copies and ring-buffer operations.
- [x] Combine volume and balance into per-buffer Q15 channel gains, leaving no
      division in the per-sample gain path. The lower-rate resampler still has
      one constant-denominator phase calculation per generated sample.
- [x] Compare the same fixtures after every change and reject regressions.

## MP3 320 kbit/s

- [x] Baseline measured for two complete 5-second windows.
- [x] Optimized measurement completed without decode errors or restarts.
- Possible: reduce wrapper/scheduling overhead; batch decoded PCM; use a faster
  decoder library only if the prebuilt Espressif decoder is the limiting cost.
- Applied: global/component `-O3`; cached stream layout; 7168-byte PCM packets;
  batched decoder yields; combined Q15 output gain; performance counters.

## AAC-LC 320 kbit/s

- [x] Baseline measured for two complete 5-second windows.
- [x] Optimized measurement completed without decode errors or restarts.
- Possible: keep AAC-LC separate from HE-AAC/SBR tests; reduce scheduling and
  PCM-copy overhead; replace the decoder only if measured CPU dominates.
- Applied: global/component `-O3`; AAC-LC-only fixture; cached stream layout;
  larger PCM batches; batched yields; combined Q15 output gain; counters.

## FLAC level 8

- [x] Baseline measured for two complete 5-second windows.
- [x] Optimized measurement completed without decode errors or restarts.
- Possible: enlarge output only on a measured `BUFF_NOT_ENOUGH`; reduce copies;
  test predictor-heavy and noise-heavy sources because bitrate alone does not
  determine FLAC decode complexity.
- Applied: global/component `-O3`; dynamically sized decode buffer; cached
  layout; larger PCM batches; batched yields; combined Q15 gain; counters.

## Ogg Vorbis quality 10

- [x] Baseline measured for two complete 5-second windows.
- [x] Optimized measurement completed without decode errors or restarts.
- Possible: separate Ogg container overhead from Vorbis decoding; reduce PCM
  copies and scheduling delays; compare another decoder only if CPU-bound.
- Applied: official Espressif Ogg/Vorbis decoder; `-O3`; cached layout; larger
  PCM batches; batched yields; combined Q15 output gain; counters.

## Ogg Opus 510 kbit/s

- [x] Baseline measured for two complete 5-second windows.
- [x] Optimized measurement completed without decode errors or restarts.
- Possible: test fixed 20 ms frames; reduce container, scheduling and PCM-copy
  overhead; evaluate decoder complexity settings with the same PCM source.
- Applied: official Espressif Ogg/Opus decoder; fixed 20 ms test frames; `-O3`;
  cached layout; larger PCM batches; batched yields; combined Q15 gain;
  counters.
