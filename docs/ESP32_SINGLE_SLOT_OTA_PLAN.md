# ESP32 single-slot OTA fallback plan

Use this plan if the required yoRadio application no longer fits in the current
OTA slots. The current two-slot layout keeps the previous application available
while a new image is written. Both measured builds fit in that layout.

## Firmware size measurements

Both native profiles were built with GCC. The comparison changes the ESP-IDF
compiler optimization from `-O2` to `-Os`. The configured codecs, TLS options,
and component-specific optimization flags were identical within each pair.

| Profile | Source revision and SDK | `-O2` app, bytes | `-Os` app, bytes | Saved, bytes | Current slot, KiB |
| --- | --- | ---: | ---: | ---: | ---: |
| ESP32-C3 OLED, tested radio profile | `da103347f`, ESP-IDF 6.1 `9a97f6c54ec6` | 1,474,272 | 1,419,328 | 54,944 | 1,856 |
| ESP32 CYD2USB, vendor codecs and PDM | `aa3103d03`, ESP-IDF 6.0.2 | 1,575,792 | 1,497,040 | 78,752 | 1,728 |

ESP-IDF's size check and esptool image validation passed for the [ESP32-C3 build](../firmware/development/esp32c3-oled-native-size-optimized/app.bin) and [CYD2USB build](../firmware/development/esp32-cyd2usb-native-pdm-size-optimized/app.bin). Hardware playback still needs qualification. In QEMU, both CYD2USB images reached `app_main` and stopped at the same Wi-Fi PHY initialization function.

## Partition layout on 4 MiB flash

Use the standard ESP-IDF second-stage bootloader, one large `ota_0` application
partition, and a small `factory` application for recovery. The recovery app
provides a Wi-Fi upload page and writes only `ota_0`. Keep the existing offsets
for NVS, `otadata`, SPIFFS, and the ESP32-C3 coredump partition.

The example reserves 768 KiB for recovery. Measure the built recovery image
before fixing the reservation. Both example layouts passed ESP-IDF partition
validation, and both measured `-Os` images passed the `ota_0` size check.

| Board | `ota_0` offset | `ota_0` size | `factory` offset | Gain over current slot |
| --- | --- | ---: | --- | ---: |
| ESP32-C3 OLED | `0x10000` | `0x2E0000` (2,944 KiB) | `0x2F0000` | 1,088 KiB |
| ESP32 CYD2USB | `0x10000` | `0x2A0000` (2,688 KiB) | `0x2B0000` | 960 KiB |

## Update and recovery

1. Install the partition table and recovery image during an initial service
   flash. Set up a board-specific GPIO entry to `factory` that clears only
   `otadata`, so recovery remains reachable even when yoRadio cannot start.
2. Have yoRadio's WebUI select `factory` as the next boot partition and restart.
   The user uploads the new `.bin` to the recovery app after it starts.
3. Stream the image to `ota_0` with `esp_ota_begin` and `esp_ota_write`. After
   `esp_ota_end` succeeds, select `ota_0` with `esp_ota_set_boot_partition` and
   restart. Application OTA leaves the bootloader and recovery image outside
   its write range.
4. Test normal boot, GPIO entry, rejected images, interrupted uploads and
   power loss before boot selection on both boards. Verify that recovery can
   accept a fresh upload and that settings and SPIFFS files survive.

An interrupted upload returns to the recovery uploader. Returning to an older
yoRadio version requires uploading its image again because the new upload
overwrites the sole yoRadio partition. [ESP-IDF OTA API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/ota.html), [bootloader factory selection](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/bootloader.html#factory-reset)
