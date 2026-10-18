# Native WebUI production qualification

All four images build from clean source `6db5651a`. CYD retains ESP-IDF 6.0.2
and Xtensa GCC15.2; C3 retains IDF revision `9a97f6c5` and RISC-V GCC15.2.
No board was flashed or reset.

| Variant | Saved application | App bytes | OTA spare bytes |
| --- | --- | ---: | ---: |
| CYD PDM | [app.bin](../../../firmware/development/esp32-cyd2usb-native-web-transfer-pdm/app.bin) | 1445296 | 324176 |
| CYD continuous DAC | [app.bin](../../../firmware/development/esp32-cyd2usb-native-web-transfer-continuous/app.bin) | 1439088 | 330384 |
| CYD legacy DAC | [app.bin](../../../firmware/development/esp32-cyd2usb-native-web-transfer-legacy/app.bin) | 1445072 | 324400 |
| C3 stereo PDM | [app.bin](../../../firmware/development/esp32c3-oled-native-web-transfer/app.bin) | 1510496 | 390048 |

Each image has its manifest, configuration, partition/project metadata and build
logs beside it. [SDK.json](SDK.json) checks application/ELF SHA256, embedded
source version, archive/build agreement and capacity against the actual slots.
The only CYD configuration changes from the previous production checkpoint are
the public pre/post WebSocket handshake callbacks. C3 additionally enables
strict RFC6455 and the project option selecting these callbacks. Board pins,
clocks, DMA, memory/socket policy and audio backend selections are unchanged.

CYD still creates `radio_stream` on core0/priority3, `audio_decode` on
core1/priority5 and `audio_output` on core1/priority6. The source assignments and
existing executable startup assertions agree; physical scheduling is not
measured here.

GCC reports zero warnings for CYD PDM, continuous DAC and C3. Legacy DAC retains
three deprecated APLL API notices in the pinned IDF5.5.4 compatibility driver;
the existing profile uses `use_apll=false`. Diagnostics and the driver remain
unchanged. The C3 multipart GCC failure and its passing refactor are recorded
separately in [HOST_GCC.md](HOST_GCC.md); the original failed build is not a
successful application qualification.

Actual target object symbols show the complete `s_clients` arrays occupy
**384 bytes on CYD** and **3200 bytes on C3**. Those include per-session message
state and command assembly buffers; the host C3 layout was 3280 bytes and must
not be substituted for target RAM. The shared TLS unit's selected static data
totals 86/90 bytes respectively, excluding linker padding and dynamic TLS/key/
session storage. Raw [CYD WS](sdk-cyd-ws-symbols.log),
[C3 WS](sdk-c3-ws-symbols.log), [CYD TLS](sdk-cyd-tls-symbols.log) and
[C3 TLS](sdk-c3-tls-symbols.log) symbol logs are retained. This is added protocol
functionality, not a RAM-saving claim.

[Host qualification](HOST.md) covers the documented message, HTTPD, upload,
actual crypto and combined WSS matrices. These builds add target compiler/link
and artifact checks. Physical HTTPS playback with WSS, multiple browsers,
slow peers, heap/DMA largest block, stack high water and interrupted provisioning
remain open. Full on-device RFC conformance and audio-safe TLS admission are
not inferred from compilation or total SoC SRAM. OTA maintenance and the
remaining transfer stages continue in the plan.
