# ESP32-C3: precise 48 kHz listening build

## Installed for user listening

The board now runs `idf61-listen48-8c1f2d`, installed through application-only
WebUI OTA on 2026-10-10. The image retains the hardware fractional divider
`2 + 1/312`, targeting nominal **48,000 PCM frames/s** instead of
48,076.923 frames/s. The user requested this mode for a listening check.
On 2026-10-10 the user reported no noticeable difference in sound after
listening. Quantitative analog noise measurements remain pending; this is
not a change to the repository's production default.

This comparison uses the **previously installed production source**, commit
`8c1f2d2d2a2c75a0f2819ae32412a29a22cda23c`, rather than introducing the newer
memory, queue or FIR experiments at the same time. The previous image remains
available for an app-only OTA return. Wi-Fi credentials and settings were
compared only in memory and were not saved in the evidence.

## Scope and verification

- Only active build-option difference: `CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK=y`.
- A frozen, build-local driver patch preserves the audited HAL divider and
  checks the supported clock configuration. The shared ESP-IDF is untouched.
- QIO 80 MHz, awake operation, original linear resampler, compact AAC/SBR/PS,
  decoder settings and production logging policy remain as installed before.
- FIR and software compensation for the integer clock are absent.
- Five existing clock tests pass. All **134 nonempty executable/constant
  sections in 19 AAC, FLAC and PCM output objects** match the previous build.
- IRAM, DRAM and RTC section sizes are unchanged. The application grows by
  **16 bytes**, from 1,446,688 to 1,446,704 bytes.
- OTA returned HTTP 200; the new app ELF identity was verified in `app1`.
  Wi-Fi, playlist and exposed settings comparisons pass. Three observations
  five seconds apart confirm resumed AAC 44.1 kHz stereo playback.

The displayed 44.1 kHz is the station's decoded PCM rate. The common hardware
output is configured for 48 kHz. This quiet build does not log clock-register
readback; its configuration and generated driver were audited. Earlier
[fractional-clock hardware testing](ESP32C3_PDM_CLOCK_20261009.md) verified
the register setup. No external frequency measurement or acoustic recording
was made in this installation, and short WebUI observations do not prove
gap-free playback.

## Images and evidence

| Item | Value |
| --- | --- |
| Installed version | `idf61-listen48-8c1f2d` |
| ESP-IDF revision | `9a97f6c54ec638111ce55cd36581b3c192f15207` |
| App SHA-256 | `798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde` |
| App ELF SHA-256 | `76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b` |
| App bytes / OTA capacity | 1,446,704 / 1,900,544 |

- [Listening app](../firmware/development/esp32c3-idf61-listen-48k/app.bin)
  and [manifest](../firmware/development/esp32c3-idf61-listen-48k/manifest.json).
- [Previous integer-clock app](../firmware/development/esp32c3-idf-6.1-r9a97-production-qio80/app.bin),
  SHA-256 `21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a`.
- [Build recipe, source hashes and installation result](../tests/results/esp32c3-pdm-listening-20261010/README.md).

## Listening result — 2026-10-10

Asked whether additional background noise, whistling or clicks appeared,
especially during quiet passages at the usual listening volume, the user
answered: "Заметной разницы не слышу" ("I do not hear a noticeable difference").
The fractional-clock image remains installed for use.

This is a subjective report on this board and audio setup. Listening duration
and the exact material were not specified. It supports the absence of an
obvious audible regression under the user's listening conditions, but does
not establish unchanged SNR/THD+N or complete codec/network qualification.
The original deployment record correctly retains its then-pending listening
status; the later [feedback record](../tests/results/esp32c3-pdm-listening-20261010/listening-feedback.json)
is saved separately.
