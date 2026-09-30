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

## Actual AAC decoder regression

Use a separate configuration, enable **yoRadio ESP32-C3 OLED → Run AAC
stream-format regression fixtures in QEMU**, and build/run it:

```powershell
.\build-qemu.ps1 -BuildDirectory build-qemu-aac `
  -Sdkconfig build-qemu-aac/sdkconfig menuconfig
.\build-qemu.ps1 -BuildDirectory build-qemu-aac `
  -Sdkconfig build-qemu-aac/sdkconfig
.\run-qemu.ps1 -SkipBuild -BuildDirectory build-qemu-aac `
  -QemuExecutable C:\path\to\qemu-system-riscv32.exe `
  -QemuBiosDirectory C:\path\to\qemu\pc-bios
```

This requires Espressif AAC and `CONFIG_YORADIO_AAC_PLUS=y`. It embeds original
synthetic fixtures from `tests/fixtures/aac_stream_format/` and executes the
actual RISC-V decoder through the production ADTS adapter. Every output frame
is checked for its rate, channel count and 16-bit sample layout, then sent to
the emulated PCM output. The shared state formatter is presented on the OLED.
The runner additionally requires `QEMU_AAC_FORMAT_PASS` for this configuration.

Cases cover AAC-LC 44.1 kHz stereo → 22.05 kHz mono → 48 kHz stereo,
HE-AAC 44.1/48 kHz stereo, HE-AAC v2 44.1 kHz stereo, and stream restart.
`QEMU_AAC_LIMITATION` records the known SDK case where SBR/PS starts after LC
with identical ADTS headers: actual core PCM is reported honestly and a restart
restores full decoding. It is not counted as successful full-rate playback.
Host tests separately execute the production callback, PCM packet, OLED snapshot
and WebSocket formatter paths (`python3 tests/run-esp32c3-stream-format.py`).
The emulator does not serve the WebUI over Wi-Fi or establish hardware CPU margin.

## AAC instruction-demand profile

In the same QEMU `menuconfig`, also enable **Count AAC decoder instructions in
QEMU (requires icount)** (`CONFIG_YORADIO_QEMU_AAC_PROFILE=y`). Rebuild and run
using the commands above. The runner detects this option in the built configuration
and adds `-icount shift=0,align=off,sleep=off`; it requires `QEMU_AAC_WORK_PASS`.

The firmware first checks `minstret` against exactly 1,024 NOPs (1,025 instructions
including the counter read). This rejects an ordinary QEMU run where the same CSR
would expose host ticks. It then measures three independent runs per fixture,
each with one unmeasured warm-up and eight measured repeats. Only ADTS/AAC decode
calls are counted; output, UI, deliberate delays and logging are outside the interval.

Summarize the log from the repository root:

```powershell
python tools/codec_benchmark/summarize_qemu_aac.py `
  idf/esp32c3-oled-native/build-qemu-aac/qemu-smoke.log `
  --output .build/aac-instruction-demand.json
```

Results are instructions per second of decoded audio, calculated from actual PCM
sample counts. A separately labelled hypothetical percentage assumes one cycle
per instruction at 160 MHz. **It is not measured ESP32-C3 CPU utilization.**
QEMU does not model instruction latency or cache/memory stalls, and this isolated
test excludes Wi-Fi/TLS and physical output. See the
[measured results and limits](../../docs/ESP32C3_AAC_CPU_PROFILE_20260930.md).
