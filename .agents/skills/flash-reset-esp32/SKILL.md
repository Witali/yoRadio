---
name: flash-reset-esp32
description: Build, flash, reset, and troubleshoot the ESP32-2432S028 CYD2USB YoRadio board over its CH340C serial adapter. Use for installing either the DAC or I2S PDM/sigma-delta YoRadio firmware, writing the SPIFFS web assets, entering the ROM bootloader, resetting the application, selecting the correct COM port, or diagnosing upload failures on this board.
---

# Flash and reset the YoRadio board

Use the scripts in this skill instead of manually toggling DTR/RTS. The board has the same verified CH340C auto-boot wiring and timing as the HLV Codec target.

## Select the serial port

1. Enumerate ports with:

   ```powershell
   [System.IO.Ports.SerialPort]::GetPortNames()
   ```

2. Identify the CH340/CH341 device from Windows PnP metadata when more than one port is present.
3. Never guess between multiple plausible ports. Ask the user if hardware metadata is ambiguous.
4. Close serial monitors and uploaders before opening the selected port.

## Flash YoRadio

From the repository root, run:

```powershell
& .\.agents\skills\flash-reset-esp32\scripts\flash_yoradio.ps1 -Port COM8 -AudioOutput DAC
```

Pass `-Esp32Sdk <path>` to compile against an isolated custom
`esp32-arduino-libs/esp32` tree. The script selects a separate
`*-custom-sdk` build directory, validates the SDK layout, and does not modify
the Boards Manager installation. Keep passing the same SDK path when using
`-SkipBuild` so the matching custom build directory is selected.

Set `-AudioOutput PDM` for the I2S0 hardware PCM-to-PDM/sigma-delta output on GPIO26. DAC is the default. The script:

- performs a clean build of `yoRadio/yoRadio.ino` for ESP32 Dev Module, 4 MB flash, Minimal SPIFFS so changes in included font data cannot be hidden by Arduino's object cache;
- installs `yoRadio/fonts/glcdfont.c` into the repository-local Adafruit GFX copy before compiling, enabling YoRadio icons and Cyrillic text;
- adds both C and C++ `I2S_INTERNAL_OUTPUT=1` overrides for PDM;
- writes bootloader, partition table, OTA boot selector, and application while preserving NVS and SPIFFS settings by default;
- uses the verified custom CH340C reset sequence;
- retries at 115200 baud if the requested faster baud fails;
- leaves the board running through esptool's final hard reset.

Use `-SkipBuild` only when the selected DAC/PDM build directory already contains matching current artifacts. Use `-WhatIf` to inspect the planned operation without building or touching the board.

Do not pass `-FlashFilesystem` during a normal firmware update. Saved Wi-Fi networks and playlists are stored in SPIFFS. Use `-FlashFilesystem` only for a first installation, partition migration, or when the user explicitly authorizes replacing those settings. The custom board table provides 512 KiB of SPIFFS at `0x370000`; each OTA application slot is `0x1B0000` bytes. The script checks the application size before flashing.

For a partition migration, download `/data/wifi.csv` and `/data/playlist.csv` from the running board first. Copy `yoRadio/data` to a temporary staging directory, place the backups in its `data` subdirectory, and pass that directory with `-FilesystemSource`. Never print the contents of `wifi.csv`. NVS at `0x9000` is never included in the flash image list.

Accept a flash as successful only when esptool exits successfully after reporting verified hashes and the final hard reset. Report the COM port, audio mode, build directory, baud rate, and verification result.

## Reset or enter the bootloader

Normal application reset:

```powershell
& .\.agents\skills\flash-reset-esp32\scripts\reset_board.ps1 -Port COM8
```

Enter the ESP32 ROM downloader:

```powershell
& .\.agents\skills\flash-reset-esp32\scripts\reset_board.ps1 -Port COM8 -EnterBootloader
```

Both commands support `-WhatIf`.

## Preserve the board timing

Do not shorten or reorder the verified control-line sequence:

- normal reset: DTR inactive, assert RTS for 200 ms, release RTS;
- ROM boot: `D0/R1` for 200 ms, then `D1/R0` for 100 ms, then `D0/R0`;
- return both lines inactive when closing the port.

If flashing fails, first confirm the port is free and still belongs to the CH340C board. Then rerun at `-Baud 115200`. Diagnose cabling or board power only after those checks.
