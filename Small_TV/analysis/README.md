# Small_TV stock firmware hardware analysis

Analyzed on 2026-10-12 from this device's `../full-flash.bin`:

```text
SHA-256: 5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4
```

The analysis is static: no application was flashed, no GPIO was driven,
and no live pin configuration or board continuity was measured.

## Application image

The partition table at flash offset `0x8000` contains NVS at `0x9000`,
PHY initialization data at `0xF000`, and one factory application at
`0x10000` with a partition size of `0x177000`. The application identifies
itself as project `hello_world`, version `1`, compiled on May 27 2026 at
23:27:57, using ESP-IDF `v5.5.4`.

| Segment | Flash data offset | Load address | Size |
| --- | --- | --- | --- |
| Flash read-only data | `0x10020` | `0x3C0C0020` | `0x3AC44` |
| Initialized RAM data | `0x4AC6C` | `0x3FCB41C0` | `0x2EC8` |
| IRAM vectors / code | `0x4DB3C` | `0x40380000` | `0x24DC` |
| Flash code | `0x50020` | `0x42000020` | `0xB29B4` |
| Additional IRAM code | `0x1029DC` | `0x403824DC` | `0x11CE0` |

Code addresses below are runtime addresses, not flash offsets. In the
flash-code segment, `flash_offset = address - 0x41FB0000`.

## Display

The factory driver contains the names `st7789_init`, `st7789_write_cmd`
and `st7789_write_data`, plus the source-file name `spi_oled.c`. Despite
that filename, the command stream and pixel format are for a colour TFT
using an ST7789-family controller, not an SSD1306-style monochrome OLED.
There is no readback of the display ID and no MISO configuration. A
specific ST7789V/ST7789VW/etc. suffix cannot be proven from this binary.

| Signal | GPIO / setting | Firmware evidence |
| --- | --- | --- |
| SCK | GPIO4 | SPI bus config at `0x42009394..0x42009396` |
| MOSI | GPIO6 | SPI bus config at `0x4200938C..0x4200938E` |
| MISO | Unused, -1 | SPI bus config at `0x42009390..0x42009392` |
| D/C | GPIO5 | Pre-transfer callback at `0x4200917C` writes transaction `user` to GPIO5 |
| RESET | GPIO1 | Reset routine at `0x420091B2` writes 0, waits 100 ms, writes 1, waits 100 ms |
| CS | Unused GPIO, -1 | Device config at `0x420093DA..0x420093DC` |
| Backlight | GPIO18 | LEDC channel config at `0x42008DA2..0x42008DA8` |

The firmware selects SPI host enum value 1 (`SPI2_HOST`), mode 3,
requested clock 40,000,000 Hz, DMA enum value 3 (`SPI_DMA_CH_AUTO`),
transaction queue length 7 and maximum transfer size 38,400 bytes.
`spi_device_polling_transmit()` sends command/data buffers; the SPI
controller generates clock and data, while the callback handles D/C.

Drawing functions at `0x4200950E` and `0x4200958A` reject x/y coordinates
greater than 239. Pixel writes send two bytes, high byte first. Thus the
firmware targets a **240 x 240 RGB565** viewport. A physical diagonal of
1.54 inches is reported by external board references, not encoded here.

The initialization sequence recovered from `0x4200934A` is:

| Command | Data | Meaning |
| --- | --- | --- |
| Hardware reset | GPIO1 low/high, 100 ms each | Reset panel |
| Delay | 150 ms | Wait after reset |
| `0x11` | none, followed by 150 ms | Sleep out |
| `0x3A` | `55` | RGB565 / 16-bit pixels |
| `0x36` | `00` | RGB order, MY/MX/MV bits clear |
| `0x2A` | `00 00 00 F0` | Initial column address range |
| `0x2B` | `00 00 00 F0` | Initial row address range |
| `0x21` | none, followed by 20 ms | Display inversion on |
| `0x13` | none, followed by 20 ms | Normal display mode |
| `0x29` | none | Display on |

The initial address-range endpoints are literally `0x00F0` (240), while
the drawing functions use valid coordinates 0..239. This is recorded as
found; the init sequence should not be mistaken for a 241 x 241 panel.
Command interpretation follows the
[Sitronix ST7789V datasheet hosted by Espressif](https://dl.espressif.com/dl/schematics/ST7789V_SPEC_V1.0.pdf).

The binary establishes no driven CS GPIO; it cannot establish that the
physical CS trace is tied to ground. The external references report that
connection, which still needs a continuity check on our unit.

## Backlight

`Backlight_pwm_init()` at `0x42008D62` initializes GPIO18 using LEDC
low-speed channel 0, timer 0, 1,000 Hz and 13-bit duty resolution.
The channel's `flags.output_invert` bit is zero. `Set_Backlight_Duty()` at
`0x42008BD2` calculates `level * 8191 / 1000` and updates channel 0.
Its initial level is 100, corresponding to duty 819, approximately 10%.

This confirms the firmware's digital control settings. It does not prove
the polarity of the board's backlight transistor or directly establish a
brightness percentage. Do not copy the active-low claim from another
revision without checking the circuit.

## GPIO availability

For the firmware's application, the candidate GPIOs without an identified
external-device assignment are **GPIO0, GPIO2, GPIO3, GPIO7 and GPIO10**.
GPIO8 and GPIO9 also have no identified application use, but are boot
strapping pins. GPIO19 and GPIO20 should remain reserved for UART0 and the
USB-UART bridge.

| GPIO | Stock firmware / board role | Availability for an extension |
| --- | --- | --- |
| 0 | No external-device use found | Candidate; also ADC1_CH0 |
| 1 | Display reset | Occupied |
| 2 | No external-device use found | Candidate; also ADC1_CH2 |
| 3 | No external-device use found | Candidate; also ADC1_CH3 |
| 4 | Display SPI clock | Occupied |
| 5 | Display D/C | Occupied |
| 6 | Display SPI MOSI | Occupied |
| 7 | No external-device use found | Candidate; JTAG alternative function |
| 8 | No application use found; boot strap | Conditional; preserve boot-time levels |
| 9 | No application use found; boot strap | Conditional; preserve boot-time levels |
| 10 | No external-device use found | Candidate |
| 11..17 | In-package flash connections | Not available on this ESP8684H package |
| 18 | Display backlight PWM | Occupied |
| 19 | UART0 RX default pin, USB-UART access | Reserved |
| 20 | UART0 TX default pin, serial console | Reserved |

These are **firmware-use findings, not a schematic or a guarantee of an
unconnected, accessible PCB pad**. The PCB has not been inspected for
pull resistors, test pads, traces or additional dormant components.
GPIO4..7 also serve JTAG functions, so debug wiring can conflict with the
display or with an extension on GPIO7. Package and strapping restrictions
come from the
[ESP32-C2 GPIO documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c2/api-reference/peripherals/gpio.html).
UART defaults are GPIO19/RX and GPIO20/TX in ESP-IDF 5.5.4's
[ESP32-C2 UART pin definitions](https://github.com/espressif/esp-idf/blob/v5.5.4/components/soc/esp32c2/include/soc/uart_pins.h).

The zero-filled `data4_io_num`..`data7_io_num` fields in the recovered SPI
structure do not assign GPIO0: octal SPI routing is not supported on C2
and those fields are ignored by this target's driver.

## Additional external devices

The external device actively configured on the user SPI bus is the TFT
panel. The stock application also configures its backlight output. The
CH340-family USB-UART bridge was independently identified during the
original serial diagnostic session.

The identified calls configure one SPI bus, one SPI device, one LEDC
timer/channel, and one GPIO mask (`0x22`, GPIO1 and GPIO5, both outputs).
The three direct `gpio_set_level()` calls belong to display reset and D/C.
No additional application pin assignment or driver initialization for an
external I2C sensor, RTC, touch controller, SD card, button input or audio
output has been identified. Generic SDK strings such as `I2C_EXT0`,
`REGI2C` and `adc_share_hw_ctrl` are not evidence of an external device.

The application contains an OpenWeatherMap weather-request endpoint;
weather data displayed on screen therefore should not be taken as proof
of a local temperature/humidity sensor. An unused speaker, battery,
microphone or sensor cannot be ruled out by static analysis alone.

The weather request routine at `0x42010864` references the endpoint string
at `0x3C0C3B58` (`http://api.openweathermap.org/data/2.5/weather`). Query
parameters, NVS settings and API-key values are not copied into this report.

## Evidence and reproduction

- [image-map.json](image-map.json): parsed partitions, application descriptor,
  segment hashes and image-integrity results.
- [display-disassembly.txt](display-disassembly.txt): exact machine-code
  instructions for the display, reset, D/C and backlight routines.
- [display-decompiled.c](display-decompiled.c): Ghidra's C-like output for
  those routines, the drawing bounds and `app_main`; whitespace normalized.
  This is not recovered original source or a buildable firmware target.
- [peripheral-callers.tsv](peripheral-callers.tsv): direct references to the
  identified configuration and transfer functions.
- [peripheral-api-references.tsv](peripheral-api-references.tsv): additional
  SDK GPIO/UART/ADC call references discovered through function-name strings.
  Identifiers may describe inlined SDK helpers; they are not a board BOM.
- [weather-endpoint-references.tsv](weather-endpoint-references.tsv): code
  reference to the weather endpoint without query parameters or credentials.
- [prepare_analysis.py](prepare_analysis.py) and
  [ExportDisplay.java](ExportDisplay.java): reproducible extraction and
  decompiler export scripts for this exact dump.

Ghidra 12.0.4 analyzed 5,144 functions using `RISCV:LE:32:default:gcc`.
Display routine names were recovered from embedded function-name strings;
names such as `st7789_set_window` and `st7789_blit_rect` were assigned during
analysis. The ESP-IDF 5.5.4 GPIO, SPI and LEDC structure layouts and API
signatures were supplied to the decompiler, then checked against the
register arguments and stack stores in GNU objdump output. In the C-like
output, helper names, variable names and types are analysis annotations;
the retained machine-code excerpt is the reference for each recovered value.

The SPI layouts can be checked in the exact-version
[spi_common.h](https://github.com/espressif/esp-idf/blob/v5.5.4/components/esp_driver_spi/include/driver/spi_common.h)
and [spi_master.h](https://github.com/espressif/esp-idf/blob/v5.5.4/components/esp_driver_spi/include/driver/spi_master.h),
and the LEDC layout in
[ledc.h](https://github.com/espressif/esp-idf/blob/v5.5.4/components/esp_driver_ledc/include/driver/ledc.h).

From the repository root, using Python 3 and the installed RISC-V GNU
objdump executable:

```powershell
python Small_TV/analysis/prepare_analysis.py --output .build/small-tv-reverse --objdump <path-to-riscv32-esp-elf-objdump>
```

The script verifies the complete dump SHA-256, partition-table MD5,
ESP application checksum and appended application SHA-256 before
extracting segments and producing an analysis-only ELF. The ELF is a
reconstruction without the original symbol/debug tables. Its synthetic
`.bss` block extends from initialized RAM to `0x3FCE0000` to represent
globals during analysis; that boundary is not a recovered application
RAM allocation. All five initialized segments retain the dump's exact
bytes and load addresses. Generated segment binaries, full disassemblies
and the Ghidra project remain under ignored `.build/`.

With Ghidra installed, create the project directory and run its headless
launcher (`analyzeHeadless.bat` on Windows) with these arguments:

```text
.build/small-tv-reverse/ghidra-project SmallTV
-import .build/small-tv-reverse/factory-analysis.elf
-processor RISCV:LE:32:default -cspec gcc
-scriptPath Small_TV/analysis
-postScript ExportDisplay.java .build/small-tv-reverse/decompiled
```

The Java script applies the audited names and structures to this image
and exports the selected C-like functions and call references. The scripts
do not reconstruct every possible indirectly called driver, execute the
application or prove physical continuity to unused GPIOs.
