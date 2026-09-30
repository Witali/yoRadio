# ESP32-C3 physical QIO test — 30 September 2026

**QIO works on the tested SuperMini OLED board at both 40 and 80 MHz.**
This was checked on physical hardware, using the SPI0 controller registers,
repeated mapped flash reads and AAC decoding. The production defaults remain
**DIO 80 MHz**; this experiment does not change the shipping flash mode.

## Board and test conditions

- ESP32-C3 QFN32 revision 0.4, embedded XMC 4 MiB flash, JEDEC ID `0x464016`.
- CPU 160 MHz, 40 MHz crystal, no PSRAM, ESP-IDF v6.0.2.
- Native USB Serial/JTAG; no deep sleep, Wi-Fi, OLED or audio-output tasks in
  the standalone diagnostic application.
- Two watchdog-reset boots per configuration. Power removal/reconnection was
  not tested.
- The initial two-byte flash status was `0x0200`: Quad Enable was already set.
  QE alone does not prove that the controller is using Quad transactions.

## Verified results

| Actual mode | SPI0 CTRL | SPI0 CLOCK | Source / divider | Complete boots | Image read checks | Result |
| --- | --- | --- | --- | ---: | ---: | --- |
| DIO 80 MHz | `0x00ac2008` | `0x80000000` | 80 MHz / 1 | 2 | 32/32 | PASS |
| QIO 40 MHz | `0x012c2008` | `0x00010001` | 80 MHz / 2 | 2 | 32/32 | PASS |
| QIO 80 MHz | `0x012c2008` | `0x80000000` | 80 MHz / 1 | 2 | 32/32 | PASS |

The test checks that exactly the expected read-mode bit is set:
`SPI_MEM_FREAD_DIO` (bit 23) or `SPI_MEM_FREAD_QIO` (bit 24), with QOUT/DOUT
read bits excluded. Clock source and divider are read from hardware using the
C3 register definitions and SDK helper at the normal PLL configuration.

Each boot verifies the application's embedded checksum/SHA-256, then maps the
entire **376,464-byte** image through SPI0/cache. It invalidates the cache before
each of 16 CRC32 passes. The host independently compares every CRC and length
against the exact saved `app.bin`, rather than accepting equal but unchecked
device results. Each configuration read **12,046,848 bytes** over two boots;
all matched. Instruction execution and the cold/warm cache probes also passed.

### Why some fields still say `dio`

ESP-IDF v6.0.2 deliberately defines `CONFIG_ESPTOOLPY_FLASHMODE="dio"` when
`CONFIG_ESPTOOLPY_FLASHMODE_QIO=y`. The ROM first loads the second-stage
bootloader using DIO; that bootloader enables QIO. The generated flashing
command and image header therefore still say DIO.

In these retained logs, `CACHE_HW_ENV flash_mode` and `FLASH_ENV configured`
report that **image-header setting**, not the running bus mode. The `ctrl`
register and the firmware assertion against the QIO/DIO boolean choice prove
the actual mode. The host validator checks these independently. Merely
changing an application header or uploading a QIO app through OTA is not this
test: the matching bootloader was installed as well.

Relevant SDK source: `components/esptool_py/Kconfig.projbuild`,
`components/bootloader_support/bootloader_flash/src/flash_qio_mode.c`, and
`components/esp_hal_mspi/esp32c3/include/hal/spimem_flash_ll.h`.

## Decoder and cache timing

Mean decoder-only CPU share in continuous mode; 24 measured windows per cell:

| Stereo fixture | DIO 80 MHz | QIO 40 MHz | QIO 80 MHz |
| --- | ---: | ---: | ---: |
| AAC-LC, 48 kHz | 16.71% | 17.42% | 14.28% |
| HE-AAC, 48 kHz | 34.61% | 35.57% | 31.20% |
| HE-AAC v2, 44.1 kHz | 42.77% | 43.96% | 38.57% |
| Cold read of 256 cache lines, CPU cycles | 83,245 | 91,949 | 48,541 |

QIO 80 MHz reduced measured decoder work by approximately **10–15% relative
to DIO 80 MHz** on these fixtures. QIO 40 MHz was slightly slower than DIO
80 MHz in this test. Clock rate and command/address overhead still matter.

The CPU percentage is `cycles / 160,000,000 / PCM seconds * 100`. Both cold
and continuous decoder runs passed, with full-rate stereo PCM and heap checks:
144 decoder windows per flash configuration, 432 in total. This is a timing
comparison of three separately configured images, not a new QEMU calibration.

These figures exclude Wi-Fi, PDM output, OLED, interrupts, fixture copies and
cache-invalidation time. They are **not total radio CPU load**. The existing
[DIO/QEMU calibration](ESP32C3_CACHE_HARDWARE_20260930.md) remains scoped to its
original image and flash mode. The calibration validator rejects these flash
experiment logs; use `analyze_flash.py` for them.

The standalone test has enough RAM for full HE-AAC/SBR/PS. It does not fix the
[full-radio SBR allocation failure](ESP32C3_AAC_MEMORY_20260930.md). Full-radio
QIO playback/OTA, long-duration operation, power-cycle startup, deep-sleep
wake-up and voltage/temperature margins were not tested here. Validate these
before making QIO the production default.

## Retained evidence and firmware

After the standalone comparison, the original DIO bootloader and application
were restored. A complete 4 MiB readback matched the private backup byte for
byte, flash status remained `0x0200`, and the original no-deep-sleep production
ELF and HTTP 200 WebUI response were verified. This restoration is recorded in
`provenance.json` before the separate full-radio QIO follow-up.

- [Six serial logs and summary](../tests/results/esp32c3-flash-quad-20260930/).
- [DIO 80 test firmware](../firmware/development/esp32c3-flash-dio80-test/).
- [QIO 40 test firmware](../firmware/development/esp32c3-flash-qio40-test/).
- [QIO 80 test firmware](../firmware/development/esp32c3-flash-qio80-test/).

Each firmware directory contains `app.bin`, the matching `bootloader.bin`,
`sdkconfig`, and a manifest with SHA-256 identities. These are standalone
diagnostic images, not normal radio firmware; they finish at
`CACHE_HW_PASS runtime=hardware` and remain awake.

## Reproduce the check

Run from the repository/task-worktree root with the configured IDF Python
and toolchain. Use one of `dio80`, `qio40`, `qio80` as `$variant`:

```powershell
$variant = 'qio80'
$build = 'idf/esp32c3-oled-native/build-flash-check'
New-Item -ItemType Directory -Force $build | Out-Null
Copy-Item "firmware/development/esp32c3-flash-$variant-test/sdkconfig" "$build/sdkconfig"
./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-flash-check `
  -Sdkconfig build-flash-check/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','../../tools/codec_benchmark/cache/sdkconfig.hardware.defaults') `
  -IdfArguments @('-D','YORADIO_HARDWARE_FLASH_TEST=ON','build')
```

Before any device write, identify the native USB port, save a private full
flash backup and flash status, and verify the partition table and active OTA
slot. This board was running `app1` at `0x1e0000`, size `0x1d0000`. Its test
write replaced only the bootloader at `0x0` and that application; no partition
table, OTA selector, NVS or SPIFFS was written. Do not use the generic whole
project `idf.py flash` command for this experiment, since it also writes the
partition table and initial OTA selector.

For this verified layout, install the **matching** bootloader and app with
esptool `write-flash --flash-mode keep --flash-freq keep --flash-size keep`.
Use the [C3 reset skill](../.agents/skills/flash-reset-esp32c3-oled/SKILL.md) to
boot, then immediately capture the diagnostic (it waits eight seconds):

```powershell
python tools/codec_benchmark/cache/capture_serial.py `
  --port COM9 --output ".build/flash-$variant-run-1.log" --timeout 60
```

Repeat each mode from a second reset. Validate the retained results without
a connected board:

```powershell
$runs = @()
foreach ($variant in @('dio80','qio40','qio80')) {
  foreach ($boot in @(1,2)) {
    $runs += @('--run', $variant.Substring(0,3), $variant.Substring(3),
      "tests/results/esp32c3-flash-quad-20260930/$variant-run-$boot.log",
      "firmware/development/esp32c3-flash-$variant-test/app.bin")
  }
}
python tools/codec_benchmark/cache/analyze_flash.py @runs --output .build/flash-summary.json
python tests/test-esp32c3-flash-quad.py
python tests/test-esp32c3-cache-hardware.py
```

For new measurements, substitute the newly captured logs and exact newly
built binary paths. The validator rejects incorrect mode/clock, corrupt or
incomplete reads, failed decoding, missing completion markers and incomplete
boot sets. The host regression tests cover these rejection paths.

After an experiment restore the original bootloader and application ranges,
compare flash readback against the backup, then verify the original radio's
WebUI and image identity. Keep backups private: full flash contains Wi-Fi and
other user settings.
