# Native OTA production qualification

All four application images build from clean source `ab1e4c6e`.
CYD retains ESP-IDF6.0.2/Xtensa GCC15.2; C3 retains the pinned IDF revision
`9a97f6c5`/RISC-V GCC15.2. No board was flashed or reset.

| Variant | Saved application | App bytes | OTA spare bytes |
| --- | --- | ---: | ---: |
| CYD PDM | [app.bin](../../../firmware/development/esp32-cyd2usb-native-ota-transfer-pdm/app.bin) | 1476672 | 292800 |
| CYD continuous DAC | [app.bin](../../../firmware/development/esp32-cyd2usb-native-ota-transfer-continuous/app.bin) | 1470672 | 298800 |
| CYD legacy DAC | [app.bin](../../../firmware/development/esp32-cyd2usb-native-ota-transfer-legacy/app.bin) | 1476672 | 292800 |
| C3 stereo PDM | [app.bin](../../../firmware/development/esp32c3-oled-native-ota-transfer/app.bin) | 1520448 | 380096 |

Each image has a manifest, sdkconfig, partition/project metadata and build
logs beside it. [SDK.json](SDK.json) checks the embedded source version,
application/ELF SHA256, archive/build agreement and OTA capacity. Every
normalized SDK configuration is exactly identical to its preceding
[WebUI checkpoint](../native-web-transfer-20261018/SDK.md). Pins, clocks, DMA,
socket limits, task priorities and backend selections are preserved.
CYD still creates `radio_stream` on core0/priority3, `audio_decode` on
core1/priority5 and `audio_output` on core1/priority6. This verifies source
assignments; physical scheduling is not measured here.

GCC reports zero compiler warnings for CYD PDM, continuous DAC and C3.
Legacy retains the same three deprecated APLL API notices from the pinned
IDF5.5.4 compatibility driver, with `use_apll=false`. C3 configuration also
retains the vendor component-validation notice about the Wi-Fi roaming
private include directory used by wpa_supplicant; it is separate from compiler
diagnostics. Build logs preserve SDK notifications and warnings.

Actual ELF DWARF layouts agree across all four targets:

| Type | Bytes | Allocation relationship |
| --- | ---: | --- |
| `native_ota_sink_t` | 4176 | Contains the4096-byte image buffer. |
| `native_ota_form_t` | 4816 | Contains the image sink and multipart state. |
| `ota_http_io_t` | 4856 | One temporary heap allocation containing the form. |
| `audio_maintenance_token_t` | 8 | Caller-owned token; owners retain no pointer. |
| `play_command_t` | 524 | Bounded URL/codec/generation command. |

These nested types must not be added together as independent allocations.
The HTTP receive chunk is a separate1024-byte local array. HTTPD task stack
requests remain6144 bytes on CYD and8192 on C3; compilation and layout do not
establish stack high water or free-heap admission on the board.

Selected target static symbols total555 bytes for CYD maintenance and retained
command state, including the524-byte command copy. C3 reuses its existing
512-byte URL and4-byte codec; the remaining selected fields total28 bytes.
The C3 single-core token-lock object has no emitted storage. These are selected
symbol sizes, excluding linker padding, other existing control state, output
backend state and dynamic allocations. Raw layouts are preserved for
[PDM](sdk-layout-cyd-pdm.json), [continuous](sdk-layout-cyd-continuous.json),
[legacy](sdk-layout-cyd-legacy.json) and [C3](sdk-layout-c3.json), each bound to
the actual ELF hash. WebSocket client arrays remain384/3200 target bytes on
CYD/C3; selected WS/TLS symbol logs are retained beside SDK.json.

[HOST.md](HOST.md) records the preceding host/software checkpoint: acknowledged
three-owner maintenance, image/form/flash fault seams, actual pinned image
verification and real HTTPD/TCP/TLS integration. This SDK checkpoint closes its
application link/export gates. QEMU has no qualified DMA-quiet contract and
does not gain positive OTA qualification from these production builds.

Physical OTA with active audio, DMA quietness, late driver cleanup, HTTP/HTTPS
heap and stack headroom, interrupted power, data preservation and boot health
remain open. The existing CYD bootloader has automatic rollback disabled;
preserving the former app slot does not enable rollback. The common chip/project
checks do not distinguish the three CYD audio variants. No signed-image,
physical flash, timing, audio quality or power-loss qualification is inferred.

The scripts used for export, target layout and qualification are frozen in
[sdk-tools](sdk-tools). They ran from the original worktree `.build/` paths
against source `ab1e4c6e`; replay requires that source and the pinned SDK/tool
paths. The campaign manifest inventories these tools, layouts and raw logs.
