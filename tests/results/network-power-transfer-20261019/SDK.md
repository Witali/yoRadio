# Network runtime and audio power: production images

Five GCC application images from clean source `489c9f81977b3bbfa6beb93c63988bc05b5b5c45`.
The full transfer remains active. These are software build/export gates;
no board was flashed or reset and no physical power or playback claim is made.

| Image | App bytes | OTA spare bytes | Saved development firmware |
| --- | ---: | ---: | --- |
| CYD PDM | 1528016 | 241456 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-power-pdm/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-power-pdm/manifest.json) |
| CYD continuous DAC | 1521808 | 247664 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-power-continuous/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-power-continuous/manifest.json) |
| CYD legacy DAC | 1527808 | 241664 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-power-legacy/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-power-legacy/manifest.json) |
| C3 stereo PDM | 1539136 | 361408 | [app.bin](../../../firmware/development/esp32c3-oled-native-network-power/app.bin), [manifest](../../../firmware/development/esp32c3-oled-native-network-power/manifest.json) |
| CYD custom FLAC, PDM | 1501536 | 267936 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-network-power-custom-flac-pdm/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-network-power-custom-flac-pdm/manifest.json) |

[SDK.json](SDK.json) checks compiler/app/ELF/configuration/metadata hashes
and unchanged CYD stream/core 0 priority 3, decoder/core 1 priority 5,
output/core 1 priority 6. The new CYD network owner retains its N1 budget
(core 0, priority 2, stack 4096); N4 adds no task or stack-budget changes.
Existing display/bootstrap bindings and C3 task priorities are preserved.

All SDK configuration values were compared with the previous time/private
Wi-Fi images. C3 is unchanged. The only new CYD keys select vendor FLAC
by default. The custom image changes exactly those two mutually exclusive
decoder selectors relative to vendor PDM. Flash, clocks, pins, Wi-Fi buffers,
socket limits and SNTP capacity remain unchanged.

[SDK-images.json](SDK-images.json) independently checks all five application
segment bounds, XOR/SHA256, descriptor/ELF identity, ESP32 chip 0 versus
ESP32-C3 chip 5, Xtensa versus RISC-V ELF machine, partition MD5/ranges and
both OTA slots. CYD uses 0x1b0000-byte slots, C3 0x1d0000.

[SDK-custom.json](SDK-custom.json) verifies the complete custom Xtensa
application link. Its ELF defines `custom_flac_decoder_feed` and omits
`esp_flac_dec_register`; vendor PDM has the opposite selection. It is an
optional development image; vendor remains the default. The unchanged
[current custom host regression](flac-after-n4/report.json) repeats 520
exact PCM comparisons, 16 lifecycle groups and three semantic controls
with all 23 frozen source hashes matching current production inputs.

PDM, continuous DAC, custom FLAC PDM and C3 have zero compiler warnings.
Legacy DAC retains the same three pinned IDF 5.5.4 APLL deprecation
warnings; the adapter still uses `use_apll=false`. Full Clang AST and
behavioral evidence remain in [README.md](README.md), which is immutable
because its bytes are bound by firmware evidence hashes.

[Actual ELF DWARF](SDK-layout.json) gives `native_network_power_snapshot_t`
20 bytes and `wifi_config_t` 184 bytes on both pinned targets. CYD
`network_profiles_t` is 481, `network_snapshot_t` 80 and `network_owner_t`
760 bytes. The shared policy has 40 bytes of named static symbols on CYD
and 32 on C3, excluding linker padding; the single-core lock is optimized
out on C3. These are target structure/symbol sizes, not simultaneous heap
peaks or measured task stack margins.

N5 hostname/AP-timeout runtime and UI integration remains open; its
persistence precursor alone is tested. [Read-only integration notes](n5-integration-plan.json)
record the checked hostname OOM behavior and the guarded reboot/OTA-lease
boundary. Custom FLAC QEMU, the remaining custom backend build matrix,
RF/DHCP/AP channel behavior, hardware DMA/heap/stack/power measurements,
memory/TLS policy and architecture-specific decoder work remain in the
[full plan](../../../docs/ESP32_CYD_C3_TRANSFER_PLAN.md).
