---
name: flash-reset-esp32c3-oled
description: Reset and recover the ESP32-C3 SuperMini 0.42-inch OLED YoRadio board over its native USB Serial/JTAG port on Windows. Use when the application must be restarted, the board is stuck in the ROM downloader after an experiment, or startup must be verified without rewriting flash, NVS, or SPIFFS. Do not use this skill for CYD boards with CH340 adapters.
---

# Reset the ESP32-C3 OLED board over native USB

Use the supplied script instead of reproducing DTR/RTS or esptool commands by
hand:

~~~powershell
& .\.agents\skills\flash-reset-esp32c3-oled\scripts\reset_esp32c3_oled.ps1 -Port COM9 -VerifyUrl http://192.168.100.4/
~~~

Do not assume COM9 or the example IP. Enumerate serial ports and identify the
board by Windows PnP ID USB\VID_303A&PID_1001. If more than one matching board
is connected, ask the user which one to reset. Close serial monitors and
uploaders before running the script.

## Choose the reset method

Watchdog is the default and preferred recovery method. It uses the
ESP32-C3-specific esptool sequence:

~~~text
--before usb-reset --after watchdog-reset run
~~~

This enters the native USB ROM interface temporarily, uploads the esptool stub
to RAM, and requests a watchdog reset into the application. It does not erase
or write flash. On Windows, pySerial may report that the device disappeared
during a successful watchdog reset. The script accepts that non-zero esptool
exit only when esptool printed "Hard resetting with a watchdog", then waits for
the USB device and performs the requested application check.

Use -Method Rts only for a simple reset while the application is already
running:

~~~powershell
& .\.agents\skills\flash-reset-esp32c3-oled\scripts\reset_esp32c3_oled.ps1 -Port COM9 -Method Rts
~~~

An RTS reset samples the BOOT strap and can return to the ROM downloader when
GPIO9 is low. Therefore it is not the preferred recovery from a stuck
downloader.

## Verify the outcome

Pass -VerifyUrl when the board's WebUI address is known. Treat the reset as
fully verified only when the script receives HTTP 2xx from that URL. Without
-VerifyUrl, report that the USB reset was issued and the port returned, but
make clear that application startup was not independently verified.

Use -WhatIf to inspect the selected board and intended method without
resetting it. Never retry indefinitely, kill unrelated processes, change boot
straps, or write firmware as part of a reset request. If the port is busy,
identify and close only the known monitor or uploader, then retry once.
