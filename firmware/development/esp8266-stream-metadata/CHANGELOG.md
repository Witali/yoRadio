# ESP8266 native: source stream metadata — 2026-09-10

Source commits: `0645c41` (channels), `8a6d2ce` (nominal AAC rate and precision).
Replaceable development build, **not a new production qualification**.

## Changes

- WebUI no longer mistakes mono PCM output for a mono source stream.
  Helix/libmad MP3 use the frame channel layout; AAC uses the decoder source
  configuration; Opus uses OpusHead. Source layout changes publish new status.
- HE-AAC status uses the existing `AACGetStreamSampRate()` (SBR nominal rate),
  independently of `AACGetSampRate()` used for actual PCM output.
- Fractional rates such as 44.1 and 22.05 kHz are displayed without floating
  point formatting. Bitrate updates are preserved.
- No changes to decoding, mono synthesis, gain, PCM stride or I2S timing.
  Callback metadata grows from 12 to 16 bytes; no extra heap/audio buffer.
- Limitation: AAC channels describe the core configuration, not undetected
  HE-AAC v2 parametric-stereo expansion. This does not add SBR/PS synthesis.

## Build and deployment

`app.bin`: 883248 bytes; SHA-256:
`F013EBC16450E6DD25C9BB109A17B087A356BEC2FDE8F0F63C8772312865F375`.

Built with `build_i2s_pdm_production.ps1 -Variant esp8266-stream-metadata
-EnableOpus -OpusWordAsm -Diagnostic -OpusStreamTest -WebAudioPause off
-NoSpiffsCache -Pdm32Iram -SdkRxDiag` (one command).
Same diagnostic profile as the installed image: CPU160, QIO40, GPIO3
I2S PDM32 DMA, 2 x 512 words, 4096-byte compressed input; SPIFFS logging off.
The Opus experiment's previous performance limitations remain out of scope.

OTA returned HTTP 200 `OK`; running slot changed from `0x110000` to
`0x10000`. Application only; no serial/reset commands or SPIFFS/settings upload.

## Verification

- 44/44 tests passed: `audio-stream-info`, `esp8266-audio-continuity`,
  `esp8266-codec-lifecycle`, `esp8266-native-websocket`,
  `esp8266-stream-input`, `esp8266-stream-metadata` (all `.test.js`).
- Input suite rerun after adding real mono MP3/AAC fixtures: 6/6 passed.
  Eight fixtures cover mono/stereo MP3 and AAC-LC, 1536/4096/6144-byte input
  buffers, queued/legacy draining and AAC block/full-frame output. PCM remains
  bit-identical between queue paths. This is not an analog sound-quality test.
- Real PCM callback and WebUI formatter tested with ASan/UBSan: source
  stereo -> mono -> stereo, format-only updates, nominal HE-AAC rate distinct
  from PCM rate, publication deduplication and failure/cancellation paths.
- Board station 284, Radio Caprice - Hard Bop:
  `http://79.111.14.76:8002/hardbop`.
  FFprobe: HE-AAC, 44100 Hz, 2 channels, measured bitrate about 48 kbit/s.
  Before: `AAC 48 kbps 22 kHz mono`.
  After: WebSocket `fmt` reported `AAC 51 kbps 44.1 kHz stereo`, then
  `AAC 48 kbps 44.1 kHz stereo`. PCM telemetry remains 22050 Hz as intended.
- During playback, status heap was 15764 bytes, allocator minimum 12688,
  WebUI stack watermark 2288. After stop: heap 27472 bytes. The current
  diagnostic configuration has very little spare IRAM (68 bytes observed).
- Playback test was only a metadata smoke test. Existing underruns were
  observed; this does **not** establish continuous or distortion-free audio.
- Browser runtime failed to initialize twice (sandbox/helper error), so no
  visual browser verification is claimed. Live WebSocket status was verified.
- Original station and stopped playback state restored after the test.

Local detailed reports: `.build/esp8266-stream-metadata-before.json`,
`-ota.json`, `-play.json`, `-after.json`, `-stop.json` (same prefix).
