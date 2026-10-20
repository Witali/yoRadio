# Production PDM ON/OFF boot: NONPASS before app_main

Both unchanged production images fail at the same SDK flash-initialization boundary. The current emulator/image pair cannot supply the proposed production-radio startup gate. No source, configuration, image, emulator, runner or input-manifest changes were made for this diagnosis, and no process was restarted.

## Observed

Root executed reserve-ON PDM (controller exit 1, chunk cc3f46) and the separately proposed reserve-OFF PDM control (controller exit 1, chunk ba06c3). Both reports record FAIL_OR_EMULATOR_LIMIT, approximately 1.031 seconds of host execution, no changed selected input, an unchanged disposable flash snapshot, and every application startup marker false. Both use the original four-MiB flash layout and the same pinned emulator/ROMs. The OFF control still has early MPI enabled.

The logs reach ROM/bootloader execution, identify the expected production project/version/ELF, select multicore application startup and initialize heap regions, then show this sequence:

    qio_mode: Failed to set QIE bit, not enabling QIO mode
    spi_flash: detected chip: gd
    spi_flash: flash io: qio
    assert failed: __esp_system_init_fn_init_flash esp_flash_spi_init.c:654 (flash_ret == ESP_OK)
    Rebooting...

QEMU exits 0 under -no-reboot when the guest requests its post-panic reboot; this is not application success. The controller correctly returns 1. There is no observed early-MPI return, display completion, audio owner creation, radio control initialization or Web service startup. Static-RX loans were not exercised.

## Source-supported interpretation

- Both saved sdkconfigs select CONFIG_ESPTOOLPY_FLASHMODE_QIO=y at 623, while the exported image/recipe header string at 630 is dio. These are different roles, not evidence that input bytes changed. [esp_flash_spi_init.c:91-93](C:/Work/yoRadio/.idf/v6.0.2/components/spi_flash/esp_flash_spi_init.c:91) derives runtime DEFAULT_FLASH_MODE=SPI_FLASH_QIO from the compile-time Boolean; a DIO boot header does not override that application setting.
- [flash_qio_mode.c:142-152](C:/Work/yoRadio/.idf/v6.0.2/components/bootloader_support/bootloader_flash/src/flash_qio_mode.c:142) emits the QIE error only when a status-register write followed by readback still lacks the required quad-enable bit. The bootloader proceeds far enough to load the application despite that earlier failure.
- The SDK system initializer calls esp_flash_init_default_chip and asserts its return at [esp_flash_spi_init.c:653-654](C:/Work/yoRadio/.idf/v6.0.2/components/spi_flash/esp_flash_spi_init.c:653). Its main-chip path prints the desired mode and then attempts chip mode setup at [esp_flash_api.c:437-452](C:/Work/yoRadio/.idf/v6.0.2/components/spi_flash/esp_flash_api.c:437). The capture proves a non-OK return, but does not expose flash_ret or the exact failing transaction.
- The observed emulator machine source chooses gd25q32 for a four-MiB drive at [esp32.c:742-745](C:/Work/QEMU-ESP32/hw/xtensa/esp32.c:742), consistent with detected chip gd. The GD SDK driver controls QE through status register2 at [spi_flash_chip_gd.c:102-126](C:/Work/yoRadio/.idf/v6.0.2/components/spi_flash/spi_flash_chip_gd.c:102). The local generic flash model does contain QE handling at [m25p80.c:828-845](C:/Work/QEMU-ESP32/hw/block/m25p80.c:828) and [1558-1563](C:/Work/QEMU-ESP32/hw/block/m25p80.c:1558); therefore this evidence does not establish that QE support is entirely absent or identify a particular controller/model defect.

The consistent ON/OFF failure, before [app_main.c:100](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32-cyd2usb-native/main/app_main.c:100), supports a flash-mode/status-register compatibility limitation of this emulator/profile combination. It does not establish a production firmware or physical-board failure, and it does not implicate static RX or early MPI. The installed executable is hash-pinned, but correspondence between the inspected local emulator source and that executable has not been independently proven.

## Gate consequence

Preserve both attempts as NONPASS. Repeating these unchanged images with this unchanged model does not qualify startup. Under the present no-change/no-hardware constraints, the full production-image QEMU gate remains unachieved at SDK flash initialization. Any emulator/model correction or hardware qualification would be separate work; none was attempted here. The focused earlier TLS target tests remain separate evidence.

## Evidence pins

Paths below are relative to this worktree. Both full reports contain the checked input/tool/source hashes.

| File | SHA256 |
| --- | --- |
| .build/cyd-production-radio-boot-pdm-01/report.json | 07eed972373403c70722e7acfab4104e56df9b11d6157d5836c62dff98959f42 |
| .build/cyd-production-radio-boot-pdm-01/qemu.log | c6b63028534396d172e532ec78891b79bed00aede0eca389b23d84bbd35edfe5 |
| .build/cyd-production-radio-boot-disabled-pdm-01/report.json | a8069905482bb0f204852e37e14fc6df026f9f870beee103a001bee7d9bbc3da |
| .build/cyd-production-radio-boot-disabled-pdm-01/qemu.log | 62387ecdf3e3cb5881f23290697889d4871330575c49fb6f3b11be5b36ea42b5 |

Additional diagnostic source SHA256 values observed read-only: SDK esp_flash_spi_init.c: 71744aba2387c911ae207e6eb92117f3eba661ba072123437d4e3db0a8cc0427; esp_flash_api.c: b3d35dde1d5296ef6fa0ec6a1e7fb0f38d3e4e4d7f9dcf68b7322892304ebbd8; spi_flash_chip_gd.c: f3d8b3f4664c2abc2e72971fd6d5fd4485807538ff0c079ce4ef6ac360e2b87f; flash_qio_mode.c: 2a473cb666373e017209ed3130e29d8971a367210b246a699791be41ee416ded; emulator m25p80.c: 6eecf0409bfc52ba9df31234144e4fa63af15122d0682a355e5350942585f99b. Original prep inputs.json retains hashes for app_main, emulator esp32/SPI sources, executable and ROMs.
