# ESP32-C3 QEMU smoke profile

This profile verifies that the ESP-IDF bootloader and application start on the
ESP32-C3 QEMU machine. It drives a controller-level SSD1306 model through the
emulated ESP32-C3 I2C FIFO and interrupt, sends a deterministic stereo test tone to its audio
backend, checks NVS settings, mounts the generated SPIFFS image, reads the
playlist fixture from it, and schedules a FreeRTOS task.

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

The runner also requires `QEMU_OLED_PASS` and `QEMU_AUDIO_PASS`, and writes the
captured 48 kHz stereo signal to `build-qemu/qemu-audio.wav`. A QEMU build with
an SDL display backend can show the scaled monochrome OLED panel in a window; the
automated runner remains headless.

The equivalent environment variables are `YORADIO_QEMU_RISCV32` and
`YORADIO_QEMU_BIOS`. Pass `-DependencyRoot` when the ESP-IDF installation is
shared with another worktree.

The SSD1306 and PCM devices validate the production OLED command/data path,
rendered display content, and decoded audio flow. ESP32-C3 I2C transfers use
the controller FIFO and interrupt path; that peripheral does not use GDMA. The
machine already includes the ESP32-C3 GDMA controller for peripherals which do
use it. QEMU does not reproduce electrical I2C timing or the physical stereo PDM
waveform. The QEMU machine still does not emulate the BOOT button, status LED,
or Wi-Fi radio. It cannot validate RF behavior, electrical pin assignments,
speaker quality, or real-time CPU margin; those still require the physical board.
Hardware debug and production builds do not enable
`CONFIG_YORADIO_QEMU` and retain their normal behavior.
