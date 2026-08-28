# ESP32-C3 QEMU smoke profile

This profile verifies that the ESP-IDF bootloader and application start on the
ESP32-C3 QEMU machine. It checks NVS settings, mounts the generated SPIFFS
image, reads the playlist fixture from it, and schedules a FreeRTOS task.

Build it separately from the hardware profiles:

```powershell
.\build-qemu.ps1
```

To merge the 4 MiB flash image, run QEMU, and require the deterministic
`QEMU_SMOKE_PASS` marker:

```powershell
.\run-qemu.ps1 `
  -QemuExecutable C:\path\to\qemu-system-riscv32.exe `
  -QemuBiosDirectory C:\path\to\qemu\pc-bios
```

The equivalent environment variables are `YORADIO_QEMU_RISCV32` and
`YORADIO_QEMU_BIOS`. Pass `-DependencyRoot` when the ESP-IDF installation is
shared with another worktree.

The QEMU machine does not emulate the board's SSD1306 display, BOOT button,
status LED, Wi-Fi radio, or stereo PDM output. The smoke profile therefore
does not start those drivers. It cannot validate audio continuity, RF behavior,
electrical pin assignments, or real-time CPU margin; those still require the
physical board. Hardware debug and production builds do not enable
`CONFIG_YORADIO_QEMU` and retain their normal behavior.
