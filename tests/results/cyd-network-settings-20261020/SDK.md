# CYD N5 and full FLAC backend matrix: SDK application exports

Six complete GCC application images from clean source `195cd3b0eb0b9a2bbb7fdf9d21b3c71302f70e86`.
No board was flashed or reset. Vendor FLAC remains the default; custom is
selected only in three explicit development images.

| FLAC | Audio output | App bytes | OTA spare bytes | Saved image |
| --- | --- | ---: | ---: | --- |
| vendor | pdm | 1542144 | 227328 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-settings-pdm/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-settings-pdm/manifest.json) |
| vendor | continuous | 1536096 | 233376 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-settings-continuous/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-settings-continuous/manifest.json) |
| vendor | legacy | 1542144 | 227328 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-settings-legacy/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-settings-legacy/manifest.json) |
| custom | pdm | 1515664 | 253808 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-settings-custom-flac-pdm/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-settings-custom-flac-pdm/manifest.json) |
| custom | continuous | 1509824 | 259648 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-settings-custom-flac-continuous/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-settings-custom-flac-continuous/manifest.json) |
| custom | legacy | 1515872 | 253600 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-settings-custom-flac-legacy/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-settings-custom-flac-legacy/manifest.json) |

[SDK.json](SDK.json) verifies every app/ELF/compiler/configuration/evidence
receipt, the ESP32 chip 0/Xtensa ELF identity, all application segments and
XOR/SHA256, partition MD5/ranges and both 0x1b0000-byte OTA slots.
Full nm logs prove `custom_flac_decoder_feed` appears only in custom images
and `esp_flac_dec_register` only in vendor images.

Every vendor SDK configuration is unchanged from its N4 backend image.
Each custom configuration differs by exactly the two FLAC selectors.
Board pins, clocks, DMA-related settings, socket limits, Wi-Fi buffers and
SNTP capacity are preserved. The three audio owners retain stream/core 0
priority 3, decoder/core 1 priority 5 and output/core 1 priority 6. Their
complete unchanged source, three-row task table and creation loop are
compared with the previous checkpoint. Display/bootstrap and the permanent
Wi-Fi owner calls, stack macros and board configuration are unchanged.

Five builds emitted zero compiler warnings. The clean custom legacy build
retains the three known IDF 5.5.4 APLL deprecation warnings; its adapter
still sets `use_apll=false`. The vendor legacy incremental build reused that
unchanged driver object and emitted no new compiler warning. The full
[52-unit Clang campaign](README.md) remains separate from GCC code generation.

[Actual final ELF DWARF](SDK-layout.json) reports network owner 936 bytes
(N4: 760), network snapshot 160 (N4: 80), settings record structure 25 and
runtime settings view 80. Profiles remain 481, Wi-Fi config 184 and power
snapshot 20 bytes. These structure sizes exclude mutex/SDK allocation costs,
allocator/RTOS overhead, simultaneous heap peaks and actual stack headroom.

The full custom backend application build/export matrix is now complete.
Custom decoder QEMU PCM/guards/lifecycle execution and physical vendor/custom
A/B, RF/DHCP/AP/restart, DMA/watchdog/heap/stack/power and long playback remain
open in the [transfer plan](../../../docs/ESP32_CYD_C3_TRANSFER_PLAN.md).
The ESP32-C3 production source was unchanged by this N5 integration; its
prior N4 image and independently repeated ordinary reboot API gate remain
recorded separately. No C3 hardware settings are imported into CYD.
