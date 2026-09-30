# ESP32-C3 stream format validation — 2026-09-30

## Changes

- Refresh decoded rate, channels and bit depth on every frame in Espressif,
  Helix/minimp3 and custom FLAC paths. PCM packets and duration accounting use
  that frame's layout, including frame-aligned 24-bit PCM chunks.
- Separate source metadata from actual PCM in the shared legacy adapter.
  Helix reports SBR's nominal rate without changing core-only PCM timing.
  Unconfirmed PS channels remain explicitly marked `core mono`.
- Publish one coherent state snapshot on changes. WebUI format updates do not
  depend on bitrate; reconnect returns current state. Stop/new generations clear
  metadata and reject stale decoder/bitrate callbacks. OLED keeps the current
  scroll snapshot but refreshes it on the next line and on Stop/Play.
- New builds use Espressif AAC Plus, including SBR/PS. The production ADTS
  adapter assembles complete frames and reopens the codec when the ADTS audio
  configuration changes. Network chunk sizes do not cause resets.
- `AAC PCM` means the API confirms decoded output only; HE-AAC/HE-AACv2 labels
  require a confirmed rate/channel expansion relative to the ADTS core.

## Executed validation

- 104 Node regression tests passed: all `esp32c3-*.test.js`,
  `custom-legacy-eos.test.js`, `audio-stream-info.test.js` and `codec-benchmark.test.js`.
- The real RTC wake-stub host test and all 16 RTC crystal pin configurations pass.

`python3 tests/run-esp32c3-stream-format.py` on WSL compiles and runs production
C/C++ with platform I/O stubs. It checks callbacks and PCM, fixed-bitrate format
changes, WebSocket status keys/reconnect, OLED snapshots, Stop/Play generation
races, bit depth, invalid decoder info and exact decimal rates. It also runs
the real Helix decoder against AAC-LC/HE-AAC/HE-AACv2 fixtures and checks the
ADTS adapter with 1..53-byte chunks, CRC headers, bad-header resynchronization,
buffer-size retry and decoder lifetime. All three executables pass.

The custom ESP32-C3 QEMU 9.2.2 runs the actual Espressif RISC-V binary codec,
the production ADTS adapter, state formatter, SSD1306 I2C driver and virtual
PCM output. Every decoded frame must match the expected layout:

| Input | PCM rate | Channels | Frames | Samples/channel |
|---|---:|---:|---:|---:|
| AAC-LC stereo | 44,100 Hz | 2 | 24 | 24,576 |
| AAC-LC mono | 22,050 Hz | 1 | 13 | 13,312 |
| AAC-LC stereo | 48,000 Hz | 2 | 26 | 26,624 |
| HE-AAC stereo | 44,100 Hz | 2 | 14 | 28,672 |
| HE-AAC stereo | 48,000 Hz | 2 | 15 | 30,720 |
| HE-AAC v2 stereo | 44,100 Hz | 2 | 15 | 30,720 |

The same adapter/generation receives these formats consecutively, without test
code resetting the codec between them. A separate restart test restores full
HE-AACv2 after the limitation below. `QEMU_AAC_FORMAT_PASS`, `QEMU_AUDIO_PASS`,
`QEMU_OLED_PASS` and `QEMU_SMOKE_PASS` are required. Fixtures are original
synthetic tones; FFprobe independently verified their profiles and layouts.

Reproduction commands: [QEMU guide](../idf/esp32c3-oled-native/QEMU.md).

## Saved production-target development images

Built from source commit `7b5d257c` with ESP-IDF v6.0.2 and Espressif audio codec
2.6.2 (`esp-adf-libs` commit `67b8d0e98f58c774b8652480893037273190e8dc`).
All images fit the existing OTA slot and have valid esptool checksums/hashes.
Each folder includes `app.bin`, SHA-256 and exact settings in `manifest.json`.

| Variant | Bytes | AAC | Deep Sleep |
|---|---:|---|---|
| [Ordinary](../firmware/development/esp32c3-oled-native-stream-format-espressif/README.md) | 1,393,488 | Espressif + SBR/PS | off |
| [Deep Sleep](../firmware/development/esp32c3-oled-native-stream-format-deep-sleep/README.md) | 1,406,352 | Espressif + SBR/PS | on |
| [Helix alternative](../firmware/development/esp32c3-oled-native-stream-format-helix-core/README.md) | 1,338,128 | Core only | on |

All use the internal RTC RC oscillator. The linked Deep Sleep images use
3,704/8,192 RTC bytes; all nine external wake-stub dependencies resolve to RTC,
ROM or GPIO registers. These are application images, not flash/NVS backups.

## Remaining limits

- The Espressif library retains core-only mode when SBR/PS appears after LC
  with **identical ADTS audio configuration**. Reproduced with LC 22.05 kHz mono
  followed by HE-AACv2 44.1 kHz stereo: actual PCM remains 22.05 kHz mono.
  This is explicitly logged as `QEMU_AAC_LIMITATION`, not accepted as successful
  full-rate decoding. Stop/Play opens a new decoder and restores 44.1 kHz stereo.
  Automatic recognition of this implicit profile change remains in the TODO.
- The public API cannot always identify an AAC profile from PCM. It must not
  claim LC/HE/PS or source channels that the decoder has not established.
- The physical board was not flashed or reset: the user requested emulator
  testing. QEMU does not emulate Wi-Fi, electrical PDM, speaker quality or
  hardware CPU timing. Full HE-AAC playback margin, TLS memory and browser/OLED
  behavior on the actual board remain to be checked.
- CYD consumes the unchanged PCM fields; adopting the new shared metadata in
  its own UI is a separate TODO. ESP8266 deployment is unchanged.
