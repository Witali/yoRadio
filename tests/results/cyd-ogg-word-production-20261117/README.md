# CYD production images with verified Ogg word storage

All six normal GCC production profiles were rebuilt from
`9d6b2708e7cd026c223cc3142de89e9db26a83a0`, after the
[full TLS/Vorbis resource fix](../cyd-vorbis-openeth-20261117/README.md).
They use ESP-IDF 6.0.2 and the normal production build entry point.

| Profile | Image bytes | Minimum free OTA bytes | Clang units | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Vendor PDM](../../../firmware/development/esp32-cyd2usb-native-ogg-word-20261117-vendor-pdm/app.bin) | 1,581,264 | 188,208 | 53 | 100 | 0 |
| [Vendor continuous DAC](../../../firmware/development/esp32-cyd2usb-native-ogg-word-20261117-vendor-continuous/app.bin) | 1,575,232 | 194,240 | 53 | 98 | 0 |
| [Vendor legacy DAC](../../../firmware/development/esp32-cyd2usb-native-ogg-word-20261117-vendor-legacy/app.bin) | 1,580,848 | 188,624 | 54 | 99 | 0 |
| [Custom FLAC PDM](../../../firmware/development/esp32-cyd2usb-native-ogg-word-20261117-custom-flac-pdm/app.bin) | 1,554,928 | 214,544 | 53 | 100 | 0 |
| [Custom FLAC continuous DAC](../../../firmware/development/esp32-cyd2usb-native-ogg-word-20261117-custom-flac-continuous/app.bin) | 1,548,784 | 220,688 | 53 | 98 | 0 |
| [Custom FLAC legacy DAC](../../../firmware/development/esp32-cyd2usb-native-ogg-word-20261117-custom-flac-legacy/app.bin) | 1,554,240 | 215,232 | 54 | 99 | 0 |

Each saved image passed chip identification, segment checksum, appended
SHA-256, exact image extent, linked ELF architecture/hash and both
`0x1b0000`-byte OTA slot checks. Compact metadata is saved beside every
image. All six SDK configuration files are byte-for-byte identical to
their pre-fix production configurations. No test translation units,
OpenETH, diagnostic certificate bundle or native diagnostics are enabled.
The exporter used `--allow-dirty` for three pre-existing untracked tests;
all tracked sources were clean.

The profiles retain mono/stereo source support and verified Ogg timelines.
Raw Opus, static TLS RX reservation, early MPI and input reclaim retain
their default disabled settings. MP3 remains Espressif; the optional
Helix mono optimization is not selected by these builds.

The stream task retains core 0, priority 3 and a 6,144-byte stack.
Decode and output retain core 1, priorities 5/6 and stacks 16,384/4,096
bytes. The [ELF frame check](../../check-cyd-ogg-stack.py) passes all six
images: `decoder_task` uses 1,760 bytes with vendor FLAC and 1,744 with
custom FLAC; the separate word-page helper uses 2,144 bytes in every
profile. These static frames do not measure total runtime stack depth.

Complete Clang analysis covers 320 project units, including the two HTTPD
overlay units in each profile, plus 20 SDK frontend checks. There are no
errors. The 13 Clang/GCC compiler/libc configuration differences match
the previous reviewed matrix. Warning counts are unchanged; one page-store
diagnostic changes class in each profile and is reviewed explicitly.
[Warning review](WARNING_REVIEW.md) · [Exact warning sites](clang-warnings.json)

The previous [ESP32-C3 image and host regression](../cyd-production-refresh-20261117/README.md)
remain the C3 checkpoint; this six-profile campaign does not rebuild C3.
The three complete TLS/Vorbis QEMU runs qualify the diagnostic application
with OpenETH. These normal board images have not been tested on physical
hardware. Wi-Fi, output timing and listening checks remain open.
[Image identities and measurements](matrix.json)
