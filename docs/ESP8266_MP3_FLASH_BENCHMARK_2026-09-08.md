# ESP8266 MP3 from internal flash, 2026-09-08

## Result

MP3 64/128 kbit/s passed 26.122 seconds of digital continuity with no
neutral-silence underruns. MP3 320 kbit/s FAILED: 286 underrun events
with Wi-Fi OFF. This does not certify live-radio/WebUI stability or
analog sound quality.

## Workload and hardware

- Physical Wemos D1 mini / ESP8266EX, CPU160, QIO40.
- Helix MP3 SSO, mono synthesis, shared reorder. No AAC is run in this matrix.
- The same self-authored 1-second stereo 44.1-kHz/16-bit WAV is encoded
  at 64/128/320 kbit/s with libmp3lame. Tones at 440/997 Hz, 200..6000-Hz
  chirp, seeded white/low-pass noise, short noise bursts, changing envelope.
  Peak -3.01 dBFS. No downloaded music or pure-silence fixture.
- All three MP3s total 66,873 bytes, embedded in mapped internal flash,
  not SPIFFS. Linker map places them at 0x402...; no whole-file RAM copy.
  Read at most 1536 bytes directly into the existing decoder input buffer.
- Decode all 40 MPEG1 frames per file sequentially, preserving the normal
  bit reservoir. Eight warmup frames, then 1000 measured frames, about
  25 loops per file. PCM is checked for nonzero samples.
- Stereo input produces mono 44.1-kHz PCM. Standard I2S PDM32 GPIO3/RX,
  2 x 512 DMA words, nominal 1.536 MHz / actual 1.538461 MHz carrier and
  the normal output rate conversion. Normalization OFF, volume 128,
  balance 0, changed only in runtime settings, not persisted.
- Wi-Fi/HTTP/WebSocket/network-stream services are disabled. No periodic
  UART printing inside the measured loop. System interrupts remain;
  the benchmark yields to RTOS every eight frames.

[Source, encoded files and generator](../tests/fixtures/mp3_composite/README.md),
[fixture hashes and encoder version](../tests/fixtures/mp3_composite/manifest.json).
Ordinary firmware does not include these test files.

## Decode-only: no PDM or DMA

| MP3 kbit/s | Total decode time, 1000 frames | Average call | Maximum call | PCM time budget | Speed |
| --- | ---: | ---: | ---: | ---: | ---: |
| 64 | 9.569528 s | 9.569 ms | 10.339 ms | 36.63% | 2.729x |
| 128 | 11.054928 s | 11.054 ms | 12.719 ms | 42.32% | 2.362x |
| 320 | 16.341901 s | 16.341 ms | 19.473 ms | 62.56% | 1.598x |

Every case: 26.122448 seconds PCM, 36,000 callbacks, nonzero PCM,
88,492 bytes free heap, 1680 bytes task stack margin. These are elapsed
decoder-call times including the PCM check and possible preemption,
NOT a system-wide CPU idle measurement. Flash reads and between-frame
RTOS yields are excluded from the decode-time sum.

## Complete flash -> decoder -> PCM -> PDM -> DMA path

| MP3 kbit/s | PCM | Wall time | DMA EOF | Underruns | Partial starts | FIFO empty | Result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 64 | 26.122448 s | 26.045376 s | 2449 | 0 | 0 | 0 | PASS |
| 128 | 26.122448 s | 26.045272 s | 2449 | 0 | 0 | 0 | PASS |
| 320 | 26.122448 s | 26.425008 s | 3089 | 286 | 1492 | 0 | FAIL |

Every case: 83,480 bytes free heap, 1480 bytes task stack margin.
Decoder memory: DRAM 8440 bytes, IRAM 16,384 bytes. These are not the
entire application's allocations. The logged workspace=25,924 is a
declared workspace size, not free heap. Fifty creates/destroys and fifty
MP3 switches returned heap to its initial value, delta=0, in both builds.

Wall time includes flash reads, RTOS and DMA waits. In this physical mode,
the decoder-call timer also includes synchronous waits in the PCM callback;
it must NOT be interpreted as decoder CPU cost.
The final DMA buffer has not necessarily drained when counters are taken;
the actual output clock also differs slightly from nominal.

Underruns count neutral PDM retries while no ready PCM is available,
NOT lost MP3 frames or the number of large audible pauses. FIFO empty=0
means DMA continued clocking, sometimes with neutral samples instead of audio.

## Interpretation and limitations

1. MP3 320 underruns reproduce without a network, so weak Wi-Fi cannot
   explain every live-radio pause.
2. Average decode speed exceeds realtime at 320, but individual decode-only
   calls reach 19.473 ms. One 512-word buffer lasts about 10.667 ms; the
   other can be only partly ready. The deadline for the next PCM block
   matters, not just average throughput. The exact missed-deadline location
   is not yet established by this matrix.
3. Next diagnostic: correlate PCM callback gaps, ready DMA words,
   flash reads and RTOS yields before changing buffer defaults.
4. Encoder priming/padding and loop boundaries can create source-level
   quiet sections. They are not underruns. PASS refers to digital counters,
   not a listening test, bit-perfect PCM proof or an analog distortion test.
5. A single synthetic clip does not cover every music signal/MPEG mode or
   worst-case workload. High-bitrate AAC was excluded.
6. The previous repeated-frame MP3-320 test selected the silent Info frame.
   Its numbers are INVALID as music-decoding benchmarks:
   [corrected historical report](ESP8266_CONTINUITY_2026-09-08.md).

## Archived evidence and reproduction

- [Physical JSON](benchmarks/esp8266-mp3-flash-2026-09-08/physical.json),
  [application UART log](benchmarks/esp8266-mp3-flash-2026-09-08/physical.log).
- [Decode-only JSON](benchmarks/esp8266-mp3-flash-2026-09-08/decode.json),
  [application UART log](benchmarks/esp8266-mp3-flash-2026-09-08/decode.log).
- [Build settings and binary hashes](benchmarks/esp8266-mp3-flash-2026-09-08/builds.json).
- Binaries/sdkconfig under firmware/development/esp8266-mp3-flash-output/
  and firmware/development/esp8266-mp3-flash-decode/: diagnostic only,
  no network services, never hand off as ordinary radio firmware.

Use the ESP8266 RTOS SDK environment and a separate build directory with
canonical sdkconfig.defaults plus these CMake settings:

    -DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=ON
    -DYORADIO_ESP8266_CODEC_RAM_MP3_MATRIX=ON
    -DYORADIO_ESP8266_CODEC_RAM_FRAMES=1000
    -DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=ON
    -DYORADIO_ESP8266_AUDIO_PROFILE=OFF
    -DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF
    -DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=OFF
    -DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=OFF

Change only CODEC_RAM_AUDIO_OUTPUT to OFF for decode-only.
After authorized app0 flashing/reset, capture at least 85 seconds for
physical / 50 seconds for decode-only. Do not transmit UART commands
on GPIO3 during output. Inspect the saved sdkconfig for exact settings.

    node tools/esp8266_audio_profile/summarize_mp3_matrix.cjs capture.log physical report.json
    node tools/esp8266_audio_profile/summarize_mp3_matrix.cjs capture.log decode report.json

The physical command exits 1 on underruns: expected for the archived 320
case. Missing/incomplete results and all-zero PCM cannot pass either.
The log archive omits only the different-baud ROM garbage before app startup.
Restore ordinary production firmware after the experiment.
