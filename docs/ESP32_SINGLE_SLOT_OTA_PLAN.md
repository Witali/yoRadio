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

Both recovery builds fit in 640 KiB, the smallest reservation aligned to 64 KiB
that keeps the data partitions at their current offsets. The C3 build has 2,848
bytes of room in `factory`. Recheck the fit after SDK or recovery changes and
move the boundary by 64 KiB if the image grows past the reservation.

| Board | `ota_0` offset | `ota_0` size | `factory` offset | Gain over current slot |
| --- | --- | ---: | --- | ---: |
| ESP32-C3 OLED | `0x10000` | `0x300000` (3,072 KiB) | `0x310000` | 1,216 KiB |
| ESP32 CYD2USB | `0x10000` | `0x2C0000` (2,816 KiB) | `0x2D0000` | 1,088 KiB |

## Recovery prototype

The [recovery project](../idf/esp32-recovery) starts a local WPA2 access point
and serves an embedded upload page. Open the board's serial console at 115200
before booting `factory` to read its network name and per-boot password. Connect
to the recovery network and open `http://192.168.4.1/`. Select the native yoRadio
`app.bin` for the board. The uploader checks the target chip and project name
before writing and checks the image and its exact length before selecting it
for boot. Recovery stores its Wi-Fi configuration in RAM.

| Target | Recovery image built with `-Os` | Size, bytes | Size, KiB | `factory` free, bytes |
| --- | --- | ---: | ---: | ---: |
| ESP32-C3 OLED | [app.bin](../firmware/development/esp32c3-recovery/app.bin) | 652,512 | 637.2 | 2,848 |
| ESP32 CYD2USB | [app.bin](../firmware/development/esp32-recovery/app.bin) | 618,448 | 604.0 | 36,912 |

ESP-IDF validated both tables and the fit of both the recovery and radio
images. esptool validated the image checksums and hashes. Host tests of the
upload handler used both native yoRadio images and mocked the HTTP and flash
APIs to check success, wrong chip, oversized or interrupted transfers, failed
writes, invalid images, and boot selection. In QEMU the ESP32-C3 image reached
HTTP route registration. The ESP32 image stopped at the same Wi-Fi PHY
initialization function as the native CYD2USB images above. Physical Wi-Fi,
browser uploads, and recovery after power loss still need board tests.

Build from `idf/esp32-recovery` with ESP-IDF 6.0.2 for CYD2USB or ESP-IDF 6.1
at `9a97f6c54ec6` for the C3 OLED. Use a separate build directory and sdkconfig
for each target.

```powershell
$target = 'esp32c3' # Use 'esp32' for CYD2USB.
$build = "../../.build/esp32-recovery-$target"
idf.py -B $build -D "IDF_TARGET=$target" -D "SDKCONFIG=$build/sdkconfig" build
```

## Update and recovery

1. Install the partition table and recovery image during an initial service
   flash. Clear `otadata` to boot `factory` for the first upload. Set up a
   board-specific GPIO entry that clears only `otadata`, so recovery remains
   reachable even when yoRadio cannot start.
2. Have yoRadio's WebUI select `factory` as the next boot partition and restart.
   The user uploads the new `.bin` to the recovery app after it starts.
3. Keep `factory` selected before starting to write, including when the
   bootloader fell back to recovery after a failed app boot. Stream the image
   to `ota_0` with `esp_ota_begin` and `esp_ota_write`. After `esp_ota_end` and
   the image length check succeed, select `ota_0` and restart.
4. Test normal boot, GPIO entry, rejected images, interrupted uploads and
   power loss before boot selection on both boards. Verify that recovery can
   accept a fresh upload and that settings and SPIFFS files survive.

An interrupted upload returns to the recovery uploader. Returning to an older
yoRadio version requires uploading its image again because the new upload
overwrites the sole yoRadio partition. [ESP-IDF OTA API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/ota.html), [bootloader factory selection](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/bootloader.html#factory-reset)
