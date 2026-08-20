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
.\tools\codec_benchmark\run.ps1 -Port COM9 `
  -BoardUrl http://192.168.100.4
```

The benchmark layout has one `0x180000` factory application and uses every byte
between it and the unchanged SPIFFS partition as a `0x240000` `codec_test`
partition. The runner writes one fixture at a time at `0x190000`, resets the
board, starts playback from flash, and captures the console result. This layout
has no OTA slots. SPIFFS remains at `0x3D0000`, so the WebUI, playlist and
`wifi.csv` stay available.

`decode/audio` below is pure decoder CPU time divided by the duration of PCM it
produced. Values below 100% keep up in isolation; lower is better. The maximum
single call and uninterrupted playback must also pass.

## Result summary

| Codec fixture | Encoded limit | Baseline | Optimized | Stable |
| --- | ---: | ---: | ---: | :---: |
| MP3 | CBR 320 kbit/s | pending | pending | [ ] |
| AAC-LC | CBR 320 kbit/s | pending | pending | [ ] |
| FLAC | level 8, noise-heavy source | pending | pending | [ ] |
| Ogg Vorbis | quality 10 | pending | pending | [ ] |
| Ogg Opus | CBR 510 kbit/s, 20 ms frames | pending | pending | [ ] |

## Common pipeline

- [x] Build the native component and firmware with `-O3`.
- [x] Measure decoder calls with `esp_timer_get_time()` in 5-second windows.
- [x] Report decoded audio duration, CPU time, real-time ratio, speed multiple,
      maximum call time and input/PCM byte counts.
- [ ] Reduce unconditional one-tick delays without starving the idle task or
      triggering the task watchdog.
- [ ] Avoid querying unchanged stream information for every decoded frame.
- [ ] Reduce PCM packet copies and ring-buffer operations.
- [ ] Replace divisions in per-sample volume, balance and resampling paths with
      fixed-point multiplies or precomputed coefficients.
- [ ] Compare the same fixtures after every change and reject regressions.

## MP3 320 kbit/s

- [ ] Baseline measured for two complete 5-second windows.
- [ ] Optimized measurement completed without decode errors or restarts.
- Possible: reduce wrapper/scheduling overhead; batch decoded PCM; use a faster
  decoder library only if the prebuilt Espressif decoder is the limiting cost.
- Applied: global/component `-O3`; integer output path; performance counters.

## AAC-LC 320 kbit/s

- [ ] Baseline measured for two complete 5-second windows.
- [ ] Optimized measurement completed without decode errors or restarts.
- Possible: keep AAC-LC separate from HE-AAC/SBR tests; reduce scheduling and
  PCM-copy overhead; replace the decoder only if measured CPU dominates.
- Applied: global/component `-O3`; integer output path; performance counters.

## FLAC level 8

- [ ] Baseline measured for two complete 5-second windows.
- [ ] Optimized measurement completed without decode errors or restarts.
- Possible: enlarge output only on a measured `BUFF_NOT_ENOUGH`; reduce copies;
  test predictor-heavy and noise-heavy sources because bitrate alone does not
  determine FLAC decode complexity.
- Applied: global/component `-O3`; dynamically sized decode buffer; counters.

## Ogg Vorbis quality 10

- [ ] Baseline measured for two complete 5-second windows.
- [ ] Optimized measurement completed without decode errors or restarts.
- Possible: separate Ogg container overhead from Vorbis decoding; reduce PCM
  copies and scheduling delays; compare another decoder only if CPU-bound.
- Applied: official Espressif Ogg decoder, `-O3`, integer output, counters.

## Ogg Opus 510 kbit/s

- [ ] Baseline measured for two complete 5-second windows.
- [ ] Optimized measurement completed without decode errors or restarts.
- Possible: test fixed 20 ms frames; reduce container, scheduling and PCM-copy
  overhead; evaluate decoder complexity settings with the same PCM source.
- Applied: official Espressif Ogg decoder, `-O3`, integer output, counters.
