# Repeat the ESP32-C3 cache measurements

Use an ESP32-C3 at 160 MHz with 4 MB DIO/80 MHz flash. This is an **opt-in
benchmark application**, with no radio, Wi-Fi, OLED updates or deep sleep.
Save the board's flash privately before replacing its app; backups contain
credentials. Never commit them. Keep the regular no-sleep app ready to restore.

## Build

From the repository root in PowerShell (replace the dependency path if needed):

```powershell
.\idf\esp32c3-oled-native\build.ps1 `
  -BuildDirectory build-hardware-cache `
  -Sdkconfig build-hardware-cache/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','../../tools/codec_benchmark/cache/sdkconfig.hardware.defaults') `
  -DependencyRoot C:\Work\yoRadio\.idf `
  -IdfArguments @('-D','YORADIO_HARDWARE_CACHE_TEST=ON','build')

New-Item -ItemType Directory -Force firmware/development/esp32c3-oled-cache-benchmark
Copy-Item idf/esp32c3-oled-native/build-hardware-cache/yoradio_esp32c3_oled_native.bin `
  firmware/development/esp32c3-oled-cache-benchmark/app.bin
```

The benchmark needs full AAC Plus. It rejects a deep-sleep configuration at
compile time. Confirm `cold_cache`, `measure_decode` and `probe` in the ELF
symbol table are in IRAM (`0x4038...` for the retained image); section attributes
alone do not prevent a compiler from inlining a routine into a flash caller.

## Hardware run

Identify the correct native USB port, save a full-flash backup, and check the
partition table and OTA selector **before** choosing an application offset.
In the retained test the active partition was app0 at `0x10000`, size `0x1d0000`.
Do not assume that offset is active on another board. Do not erase flash or use
the full `flash` target: that would replace partitions, OTA selection and SPIFFS.

With an activated IDF Python environment, for that verified app0 layout:

```powershell
python -m esptool --chip esp32c3 -p COM9 -b 460800 `
  --before usb-reset --after no-reset write-flash `
  0x10000 firmware/development/esp32c3-oled-cache-benchmark/app.bin

.\.agents\skills\flash-reset-esp32c3-oled\scripts\reset_esp32c3_oled.ps1 -Port COM9
python tools/codec_benchmark/cache/capture_serial.py --port COM9 `
  --output .build/cache-hardware/hardware-run-1.log
```

The app waits eight seconds for the passive USB reader. Require
`CACHE_HW_PASS runtime=hardware`; port enumeration alone is insufficient.
Repeat reset/capture to `hardware-run-2.log`. The completed bench stays awake.
Restore the regular app and verify its WebUI before leaving the board.

## Same application in QEMU

Create a **clean synthetic** image, never an image from the private board backup:

```powershell
$b = 'idf/esp32c3-oled-native/build-hardware-cache'
python -m esptool --chip esp32c3 merge-bin --output .build/cache-hardware/qemu-flash.bin `
  --flash-mode dio --flash-size 4MB --flash-freq 80m --pad-to-size 4MB `
  0x0 "$b/bootloader/bootloader.bin" 0x8000 "$b/partition_table/partition-table.bin" `
  0xe000 "$b/ota_data_initial.bin" 0x10000 firmware/development/esp32c3-oled-cache-benchmark/app.bin

& 'C:\path\to\qemu-system-riscv32.exe' -M esp32c3 -nographic -no-reboot -snapshot `
  -icount shift=0,align=off,sleep=off -L 'C:\path\to\share\qemu' `
  -drive file=.build/cache-hardware/qemu-flash.bin,if=mtd,format=raw `
  *> .build/cache-hardware/qemu-run-1.log
```

Repeat into `qemu-run-2.log`. The tested yoRadio fork is QEMU 9.2.2,
revision `413834d79a1ac46570cdf4839f136e3b9a8e6ffd`. Its PCER CSR reads zero;
hardware IDF startup selects cycle event 1. This exact fork behavior selects
UART output and `minstret` in QEMU, USB output and the cycle counter on hardware.
Do not assume this detection works with an arbitrary emulator. Require the NOP
check (1,025 instructions) and `CACHE_HW_PASS runtime=qemu`.

## Validate and summarize

```powershell
python tools/codec_benchmark/cache/analyze_hardware.py `
  --hardware .build/cache-hardware/hardware-run-1.log `
  --hardware .build/cache-hardware/hardware-run-2.log `
  --qemu .build/cache-hardware/qemu-run-1.log `
  --qemu .build/cache-hardware/qemu-run-2.log `
  --output .build/cache-hardware/summary.json
python tests/test-esp32c3-cache-hardware.py
```

See the [hardware report](../../../docs/ESP32C3_CACHE_HARDWARE_20260930.md)
for the timing boundaries, measured factors and limitations. The older AAC
calibration CLI still uses its historical 320 kbit/s reference; this experiment
does not silently replace that factor.
