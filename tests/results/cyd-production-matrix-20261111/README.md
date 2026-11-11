# CYD production matrix and ESP32-C3 regression, 2026-11-11

The six CYD GCC application images were linked and checked against the original
dual-core task configuration, board profile and two `0x1b0000`-byte OTA slots.
The common CYD source is `aa3103d0361c5f57afb021e124851bc5a09666c8`. The later
production source edit is confined to the ESP32-C3 include in `audio_service.c`.

| CYD variant | Application bytes | Free bytes per OTA slot | Clang units | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Vendor PDM](../../../firmware/development/esp32-cyd2usb-native-ogg-final-20261104-vendor-pdm/app.bin) | 1,575,792 | 193,680 | 53 | 97 | 0 |
| [Vendor continuous DAC](../../../firmware/development/esp32-cyd2usb-native-ogg-final-20261104-vendor-continuous/app.bin) | 1,569,584 | 199,888 | 53 | 95 | 0 |
| [Vendor legacy DAC](../../../firmware/development/esp32-cyd2usb-native-ogg-final-20261111-vendor-legacy/app.bin) | 1,575,344 | 194,128 | 54 | 95 | 0 |
| [Custom FLAC PDM](../../../firmware/development/esp32-cyd2usb-native-ogg-final-20261111-custom-flac-pdm/app.bin) | 1,549,936 | 219,536 | 53 | 97 | 0 |
| [Custom FLAC continuous DAC](../../../firmware/development/esp32-cyd2usb-native-ogg-final-20261111-custom-flac-continuous/app.bin) | 1,543,696 | 225,776 | 53 | 95 | 0 |
| [Custom FLAC legacy DAC](../../../firmware/development/esp32-cyd2usb-native-ogg-final-20261111-custom-flac-legacy/app.bin) | 1,549,488 | 219,984 | 54 | 95 | 0 |

The first two GCC rows and the vendor PDM Clang profile are the completed runs
from the [4 November checkpoint](../cyd-transfer-pause-20261104/README.md). The
resumed campaign revalidated the remaining 233 tool and SDK bindings and all
118 pinned inputs after the PowerShell update. Its wrapper checks passed with
the current PowerShell. The initial preflight rejection and all raw receipts
are retained locally. Every Clang configuration has the same reviewed 13-entry
compiler and libc delta. Each CYD profile also checked the SDK HTTP client,
ESP-TLS and Mbed TLS frontends. The two legacy profiles additionally checked
the borrowed ESP-IDF 5.5.4 driver.

The ESP32-C3 include now resolves directly to the shared fairness header. The
GCC object dependency record contains that exact file. The linked ESP32-C3
image at `b7e8fee03113d81c4267fa8f5e6ba5cdaba8ae9a` passed the RISC-V ELF,
ESP32-C3 header, checksum, validation hash and OTA geometry checks. It is
1,680,464 bytes with 220,080 bytes free per `0x1d0000`-byte slot. Enabling
Git long path handling in the build process corrected the app version label.
The corresponding ESP-IDF 6.1 Clang run checked 61 units and three SDK
frontends with 117 warnings and zero errors. The ASan/UBSan host regression
matched all six PCM/metadata comparisons and the prior variant and normalizer
results, including 648 exact normalizer cases. [ESP32-C3 image](../../../firmware/development/esp32c3-oled-native-cyd-transfer-20261111/app.bin)

The current vendor PDM image reached `app_main` and ST7789 initialization in
the pinned dual-core QEMU with the 25 ns SPI input-delay profile. The guest
then panicked at `0x60033c00`. The exact ELF resolves the failing instruction
to `register_chipv7_phy` through `esp_phy_load_cal_and_init`. QEMU returned
zero and the startup result is **NONPASS**. The offline flash image and its
component bindings matched before and after the run. Complete radio startup,
combined radio/TLS/TFT resource measurements, physical DMA and listening tests
remain open.

[matrix.json](matrix.json) records the exact image and receipt identities.
[clang-warnings.json](clang-warnings.json) lists each profile's warning sites
and multiplicities. [Warning review](WARNING_REVIEW.md) records the additional
review and focused regression. Full logs, compiler dependency records and
binary build intermediates remain in the local verification directories.
