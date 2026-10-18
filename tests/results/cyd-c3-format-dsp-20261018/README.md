# Integrated CYD format, bitrate and DSP qualification

The deferred format/bitrate block was resumed and completed in software.
CYD reports precise decoder PCM layout and ICY/decoder/measured bitrate with
generation-safe source priority. C3 uses the same portable meter and serialized
publication. Normalization and its HTTP settings are integrated on CYD while
retaining its mono output and three existing hardware backends.

## Executable evidence

- [CYD stream/metadata](../cyd-stream-format-20261018/README.md) and the final
  [51 stream + 80 settings requests](http-settings-final/report.json).
- [C3 bitrate state](../c3-bitrate-state-20261018/README.md): eight passing groups,
  six focused old-source assertions, state/command regressions and full format suite.
- [CYD normalizer](../cyd-normalizer-20261018/README.md): actual output producers,
  original DSP reference, immutable unaligned PCM, reset/rate/layout/EOF,
  disabled-path identity and six integrated pipeline variants.
- Final [C3](startup-c3/report.json) and [CYD](startup-cyd/report.json) startup
  corpora both pass 34 cases. Quiet/diagnostic 32/64-bit
  [health regressions](health/report.json) also pass.
- [Production-wrapper host tests](../cyd-production-wrapper-20261018/README.md)
  have 38 passes and one Windows directory-symlink skip. Real build/export
  qualification below complements those fixtures.

## Pinned SDK builds

| Target/backend | Clean source | App bytes | Saved manifest |
| --- | --- | ---: | --- |
| CYD PDM | `e1b1539a` | 1,384,736 | [firmware](../../../firmware/development/esp32-cyd2usb-native-format-dsp-pdm/manifest.json) |
| CYD continuous DAC | `e1b1539a` | 1,378,672 | [firmware](../../../firmware/development/esp32-cyd2usb-native-format-dsp-dac/manifest.json) |
| CYD legacy DAC | `e1b1539a` | 1,384,784 | [firmware](../../../firmware/development/esp32-cyd2usb-native-format-dsp-legacy/manifest.json) |
| C3 tested radio | `8c302697` | 1,475,696 | [firmware](../../../firmware/development/esp32c3-oled-native-format-bitrate/manifest.json) |

All three CYD builds use the new production wrapper and IDF 6.0.2; C3 uses its
pinned IDF 6.1 revision `9a97f6c5`. Every image agrees with its manifest, embedded
version and ELF digest. Normalized SDK configuration is identical to each
target/backend's preceding checked profile. CYD partition bounds are verified
from its real partition table; app/bootloader/NVS/SPIFFS are not deployed.
The C3 compatibility include exposes the portable meter on its actual SDK path.

[Qualification data](qualification.json) includes hashes, config comparisons
and actual Xtensa symbol sizes. The CYD DSP objects sum to 554 DRAM bytes:
512 scratch, 24 normalizer instance, 12 configuration cache, 4 sample rate and
two one-byte state flags, excluding linker padding and other metadata state.
The limiter LUT occupies 1,170 bytes in flash `.rodata`. This is linked resource
usage, not a measurement of available runtime heap or CPU load.

## Full static analysis

[CYD](../native-lint-20261018/cyd-format-dsp/report.json) completes all 20 own
units with 11 warnings and zero errors; [C3](../native-lint-20261018/c3-format-bitrate/report.json)
completes all 50 with 97 warnings and zero errors. The file/check/message finding
sets match their preceding full baselines, and new normalizer units have no
findings. No checks were disabled. Physical audio/network/DMA acceptance,
remaining PCM layouts, full WebUI/OTA and later transfer stages remain open.
