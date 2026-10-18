# Time and private Wi-Fi: target SDK qualification

2026-10-18. Four GCC production images from clean source
`8bcacfe955ccb545baf7e7cf5fef5252c8300630`. Application/ELF hashes, embedded ELF identity,
saved SDK configuration and available OTA space are verified in
[SDK.json](SDK.json). Host behavioral and lint evidence is in [HOST.md](HOST.md).
No board was flashed or reset for this checkpoint.

| Image | App bytes | OTA spare bytes | Saved firmware |
| --- | ---: | ---: | --- |
| CYD PDM | 1518704 | 250768 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-runtime-transfer-pdm/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-runtime-transfer-pdm/manifest.json) |
| CYD continuous DAC | 1512528 | 256944 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-runtime-transfer-continuous/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-runtime-transfer-continuous/manifest.json) |
| CYD legacy DAC | 1518576 | 250896 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-runtime-transfer-legacy/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-runtime-transfer-legacy/manifest.json) |
| C3 stereo PDM | 1538352 | 362192 | [app.bin](../../../firmware/development/esp32c3-oled-native-runtime-transfer/app.bin), [manifest](../../../firmware/development/esp32c3-oled-native-runtime-transfer/manifest.json) |

All configurations are compared with the preceding OTA checkpoint. The
only CYD change is `LWIP_SNTP_MAX_SERVERS: 1 -> 2`, required by the two-server
time service. C3 configuration is unchanged. The production wrapper applies
that minimum only in each isolated build configuration; prior images and
external seed files remain intact. Existing flash, Wi-Fi buffers, socket limits,
audio backend, GPIO and SDK selections remain as in those qualified profiles.

CYD stream stays on core 0 / priority 3, decoder on core 1 / priority 5 and
output on core 1 / priority 6. Existing display/network bootstrap bindings
are also covered by the actual startup/event host campaign. These are
source/build checks, not physical task scheduling measurements.

Actual final ELF DWARF sizes are recorded in [SDK-layout.json](SDK-layout.json).
They describe target structures, excluding allocator/RTOS overhead; they
do not establish simultaneous allocation peaks or free heap/stack margin.

| Structure | CYD bytes | C3 bytes |
| --- | ---: | ---: |
| `native_time_sntp_config_t` | 74 | 74 |
| `native_wifi_edit_t` | 580 | 580 |
| `native_wifi_metadata_t` | 220 | 220 |
| `native_wifi_request_io` | 64 | 64 |
| `private_workspace_t` | 1284 | 1284 |
| `wifi_http_payload_t` | 4676 | 4676 |

The symbol logs preserve actual linked-target object symbol sizes for
network/time, Wi-Fi owner/HTTP/I/O, shared SNTP, WebSocket and TLS units.
They are a baseline for later CYD memory work, not an optimization or
physical performance claim.

Compiler warning instances per image: CYD PDM 0, CYD continuous DAC 0, CYD legacy DAC 3, C3 stereo PDM 0.
The legacy DAC build retains pinned IDF 5.5.4 deprecated APLL API warnings;
its existing configuration disables those APLL branches. Raw build logs
and compiler/configuration identity accompany each development image.
SDK/Kconfig and CMake advisories remain visible in those logs; they are
separate from the compiler-warning counts above.

Experimental Xtensa Clang 20.1.1 optimized code generation remains affected
by the recorded `time_settings_valid` vector instruction-selection crash.
Complete clang-tidy AST analysis and these production GCC builds pass
separately. No production source workaround or warning suppression was added.

Remaining gates include runtime profile/reconnect/RSSI/power integration,
physical RF/AP and clock behavior, flash power loss, TLS/audio/TFT resource
measurements and long-running playback. Custom CYD FLAC runtime and private
Xtensa codec ABI work remain separate plan stages.
