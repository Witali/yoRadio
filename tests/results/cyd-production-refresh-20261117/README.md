# CYD production refresh and ESP32-C3 regression

All seven GCC images were built from `f72600f1add2da21aca1c6ff159c9e1abebed021`
through the normal production entry points. The six CYD builds cover
Espressif and custom FLAC on PDM, continuous DAC and legacy DAC. The CYD
images use ESP-IDF 6.0.2 and the C3 image uses the pinned 6.1 revision.

| Profile | Image bytes | Minimum free OTA bytes | Clang units | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| [CYD vendor PDM](../../../firmware/development/esp32-cyd2usb-native-transfer-20261117-vendor-pdm/app.bin) | 1,581,408 | 188,064 | 53 | 100 | 0 |
| [CYD vendor continuous DAC](../../../firmware/development/esp32-cyd2usb-native-transfer-20261117-vendor-continuous/app.bin) | 1,575,392 | 194,080 | 53 | 98 | 0 |
| [CYD vendor legacy DAC](../../../firmware/development/esp32-cyd2usb-native-transfer-20261117-vendor-legacy/app.bin) | 1,580,992 | 188,480 | 54 | 99 | 0 |
| [CYD custom FLAC PDM](../../../firmware/development/esp32-cyd2usb-native-transfer-20261117-custom-flac-pdm/app.bin) | 1,553,312 | 216,160 | 53 | 100 | 0 |
| [CYD custom FLAC continuous DAC](../../../firmware/development/esp32-cyd2usb-native-transfer-20261117-custom-flac-continuous/app.bin) | 1,547,344 | 222,128 | 53 | 98 | 0 |
| [CYD custom FLAC legacy DAC](../../../firmware/development/esp32-cyd2usb-native-transfer-20261117-custom-flac-legacy/app.bin) | 1,552,912 | 216,560 | 54 | 99 | 0 |
| [ESP32-C3 production](../../../firmware/development/esp32c3-oled-native-transfer-20261117/app.bin) | 1,523,776 | 376,768 | 61 | 122 | 0 |

Each image passed the Espressif image parser, segment checksum, appended
SHA-256, chip identification, linked ELF architecture/hash and both OTA
partition checks. Compact metadata is saved beside each application.
The exporter used `--allow-dirty` for three pre-existing untracked test
files. All tracked sources were clean. The compilation databases contain
zero test translation units.

The CYD profiles retain the normal two-channel policy. Packet-level Opus,
static TLS RX, early MPI, reclaim and native diagnostics use their default
disabled settings in this matrix. Their runtime tests are recorded in
the [DAC matrix](../cyd-opus-dac-matrix-20261117/README.md) and
[PDM boundary tests](../cyd-ogg-page-maximum-20261117/README.md).
The CYD stream task uses core 0, priority 3 and a 6,144-byte stack.
Decode and output use core 1, priorities 5/6 and stacks 16,384/4,096 bytes.

The complete Clang analysis covered 381 project units, both generated HTTPD
overlay units in every profile, and 23 SDK frontend checks. The CYD
Clang/GCC configuration difference matches the reviewed 13 compiler/libc
settings. The C3 difference is also confined to compiler/libc settings.
Warnings remain available for review.
[Warning analysis](WARNING_REVIEW.md) · [All warning sites](clang-warnings.json)

The C3 build uses its canonical production console/logging policy.
Compared with the older diagnostic image, 19 settings disable console
output, boot/runtime logging and printed panic output. The normalizer and
staged/DMA host regression passed all six PCM/metadata comparisons and
648 exact normalizer cases under ASan and UBSan.

The SDK check found zero tracked changes in ESP-IDF 6.0.2, 5.5.4 and the
pinned 6.1 source. Full build and analysis logs stay local. Physical
Wi-Fi, output timing and listening tests still require the boards.
[Measurements and image identities](matrix.json)
