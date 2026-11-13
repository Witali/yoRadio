# Continuous DAC production build and QEMU check

The [production application image](../../../firmware/development/esp32-cyd2usb-native-dac-write-20261113/app.bin)
was built from `3f06c58d0f1af5cc8cf7a94091126eb58634f248` with ESP-IDF 6.0.2
and the [production wrapper](../../../idf/esp32-cyd2usb-native/PRODUCTION_BUILD.md).
The image fits both OTA slots with 199,696 bytes free in each. Its
[metadata](../../../firmware/development/esp32-cyd2usb-native-dac-write-20261113/app-metadata.json)
records the image and configuration hashes. The build uses Wi-Fi, static TLS
buffers, the default CYD TCP settings, and the five-second task watchdog.

Continuous DAC compiles the generated driver in the original ESP-IDF
component. Its source hash matches the [qualified DMA overlay](../cyd-openeth-dac-wait-20261113/README.md).
PDM and legacy DAC still compile the original SDK source. All five host
ASan/UBSan cases pass. The negative control still catches the old DMA start
order.

The [OpenETH QEMU fixture](../../target/cyd_full_app_openeth_qemu/README.md)
uses the same CMake hook and generated driver as the production build. It
uses dynamic TLS buffers, the C3 TCP window and mailbox, and a 30-second task
watchdog. The sequential continuous DAC run completed 43 full TLS 1.2
records, flushed exactly 528,000 PCM frames at EOF, and served the same
WebUI asset during playback and after EOF. It reported zero allocation or
output failures and a minimum free heap of 6,208 bytes.

Two earlier full-record attempts using the same QEMU application image timed
out after at least 39,048 and 43,848 PCM frames respectively. One
ordinary-record attempt timed out before playback. The legacy DAC control
with the C3 TCP settings reported one failed 2,048-byte allocation and one
output configuration error before the first PCM write.

The [run summaries](observed.json) retain all five outcomes and their hashes.
Physical Wi-Fi playback and hardware audio output remain pending.
