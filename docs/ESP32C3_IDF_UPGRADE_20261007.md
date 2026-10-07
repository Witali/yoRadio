# ESP32-C3 sequential ESP-IDF upgrade

## Scope and sequence

Starting point: main `ff490cd4`, installed production image built from
`a06181cf` with ESP-IDF 6.0.2. Keep the saved image under
`firmware/development/esp32c3-main-production-20261007` available for rollback.

1. Record physical 6.0.2 format, EOF, transition, fault and WebUI controls.
2. Install 6.0.3 beside 6.0.2; build and test before advancing the SDK pin.
3. Install 6.1 separately; apply required API migrations and repeat the tests.
4. Save both sets of outcomes, binary/configuration hashes and comparisons;
   retain failures and distinguish regressions from failures present on 6.0.2.
5. Leave the board on a verified production image and preserve its Wi-Fi,
   playlist and settings. Do not overwrite an existing versioned release.

`idf/esp32c3-oled-native/idf-version.txt` is the SDK pin used by setup, build
and the dependent QEMU/benchmark tools. Each SDK has its own checkout,
tool directory and build directories. The audio-codec archive stays pinned
to the same revision so the SDK comparison does not also change the decoder.

## Validation matrix for each SDK

- Clean production and profiling builds; compile deep-sleep and external-32k
  variants. The connected board has no external crystal, so the crystal
  variant receives a build check only.
- C3/shared Node regressions, Python evidence/parser/ABI tests, ASan/UBSan
  stream-format, decoder ownership and EOF tests; SDK-specific lwIP checks.
- QEMU decoder PCM, retry and allocation-failure checks using the target SDK.
- Physical MP3, AAC-LC, HE-AAC, HE-AACv2, FLAC, Vorbis and Opus file matrix,
  explicit/AUTO selection, natural EOF, format transitions and Stop/Play.
- WebSocket reconnect/format consistency, reboot, network faults, configured
  availability timeout and settings persistence.
- OTA upgrade and repeatability, invalid-image rejection, interruption and
  slow upload; verify the running image and preserved settings/files.
- CPU/heap under HTTP load, codec switching, HTTP/HTTPS station playback and
  ten-minute sustained playback. CPU usage is recorded without an 85% limit.
- Production-image OTA and saved-station playback at the end of each stage.

Automated status/PCM/DMA evidence does not replace listening or a visual OLED
check. Manual observations and unavailable test prerequisites are reported
separately. Historical experiment evidence replay is not a new hardware run.

## Migration references

- [ESP-IDF 6.0.3 release notes](https://github.com/espressif/esp-idf/releases/tag/v6.0.3):
  HTTP-server Content-Length handling and request body size limit change.
- [ESP-IDF 6.1 release notes](https://github.com/espressif/esp-idf/releases/tag/v6.1).
- [6.1 migration guide for ESP32-C3](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/migration-guides/release-6.x/6.1/index.html).

## Execution status

In progress. Results will be added as each stage completes; a planned check
is not a passed check.

### 6.0.3 lwIP source audit

The first clean build correctly rejected the changed `api_msg.c` hash.
Compared with 6.0.2, this file only changes DNS result-count handling;
close/shutdown paths and `tcp.c` are unchanged. Added its exact normalized
source hash to the allowlist, retaining rejection of all unaudited sources.
SDK submodule revision: `c6f2f878e7b0f86033214b85547d579be43351e3`.

The actual 6.0.3 stack passed all six half-close scenarios with ASan/UBSan
for both heap and pool allocation after our fix (12 passes). Both unpatched
controls still fail the five ownership cases and pass the ordinary full-close
case. This demonstrates that the local fix is still needed on 6.0.3.
