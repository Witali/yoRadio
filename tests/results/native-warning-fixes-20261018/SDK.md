# SDK build qualification

All four production images build from clean source `3b8e5d2ffdbee4379c252ed7482f16ab269a2a10`.
CYD uses the pinned ESP-IDF 6.0.2/Xtensa GCC 15.2; C3 uses the pinned
ESP-IDF 6.1 revision 9a97f6c5/RISC-V GCC 15.2. No board was flashed.

| Variant | Image | App bytes | OTA spare bytes | Metadata |
| --- | --- | ---: | ---: | --- |
| CYD PDM | [app.bin](../../../firmware/development/esp32-cyd2usb-native-startup-web-pcm-pdm/app.bin) | 1412128 | 357344 | [manifest](../../../firmware/development/esp32-cyd2usb-native-startup-web-pcm-pdm/manifest.json) |
| CYD continuous DAC | [app.bin](../../../firmware/development/esp32-cyd2usb-native-startup-web-pcm-dac/app.bin) | 1405952 | 363520 | [manifest](../../../firmware/development/esp32-cyd2usb-native-startup-web-pcm-dac/manifest.json) |
| CYD legacy DAC | [app.bin](../../../firmware/development/esp32-cyd2usb-native-startup-web-pcm-legacy/app.bin) | 1412000 | 357472 | [manifest](../../../firmware/development/esp32-cyd2usb-native-startup-web-pcm-legacy/manifest.json) |
| C3 stereo PDM | [app.bin](../../../firmware/development/esp32c3-oled-native-warning-fixes/app.bin) | 1476592 | 423952 | [manifest](../../../firmware/development/esp32c3-oled-native-warning-fixes/manifest.json) |

[Machine-readable checks](SDK.json) verify source version, image/ELF SHA-256,
archive/config agreement, partition capacity and changes from the preceding
profiles. CYD adds native WebUI settings and WebSocket support while retaining
its board, clock, DMA and socket profiles. The tested C3 configuration is
identical to its preceding archived profile. Exact configuration differences
and compiler warning lines are retained in the JSON report.

GCC reports zero warnings for C3, CYD PDM and continuous DAC. Legacy DAC has
three `-Wdeprecated-declarations` warnings in the pinned ESP-IDF 5.5.4
`i2s_legacy.c` compatibility driver, for its APLL acquire/set/release helpers.
The existing backend sets `use_apll = false`; those APLL branches are disabled
in this profile. These are API migration notices, with no reproduced runtime
failure. The driver and diagnostics remain unchanged.

The PDM ELF contains 555 bytes of selected normalizer/layout DRAM symbols and
1254 bytes of lookup tables in mapped flash, including the 1170-byte soft-limit
LUT. Symbol sizes exclude linker padding and do not measure runtime free heap.

CYD preserves the original pinned audio tasks: `radio_stream` on core 0 at
priority 3; `audio_decode` on core 1 at priority 5; `audio_output` on core 1 at
priority 6. The startup harness asserts these assignments in every variant.

The CYD wrapper archives build logs, config, partition and project metadata;
C3 retains the corresponding files beside its image. See [host qualification](HOST.md)
and the earlier [startup/PCM/WebUI qualification](../cyd-startup-pcm-web-20261018/HOST.md).
No physical network/audio/browser, heap/stack headroom or power-loss acceptance
is claimed. AAC owner-view qualification and the remaining transfer stages
stay open in the plan.
