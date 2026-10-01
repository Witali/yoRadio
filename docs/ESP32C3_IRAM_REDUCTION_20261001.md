# ESP32-C3 IRAM placement audit — 2026-10-01

**Later qualification failure:** the follow-up
[Wi-Fi buffer experiment](ESP32C3_WIFI_BUFFER_BALANCE_20261001.md) records an
`Illegal instruction` panic during OTA from this audit's Auto Suspend image.
The larger relocation profile must remain disabled pending diagnosis. The
successful runs below are retained historical evidence, not an all-clear.

## Scope and acceptance

The objective is to make more internal SRAM available as DRAM **without
removing functionality**. Compare the same firmware sources and codec options;
do not count unsupported AAC core-only output as successful HE-AAC. Preserve
Flash encrypted-operation APIs as well as all codec formats, rates and channels.
Do not infer interrupt latency, audible continuity or production qualification
from a successful build or a larger heap alone.

Source baseline: `87c775c3`, ESP-IDF 6.0.2, ESP32-C3 rev. 0.4 with embedded
XMC-D Flash, JEDEC `0x464016`, DIO 80 MHz. All comparison builds use compact
service stacks, six dynamic Wi-Fi RX/TX buffers and HTTP-driven CPU counters.
They use the unchanged native AAC owner: no early scratch, PS relocation,
PC16 quantization or unpacked-value cache. Deep sleep is disabled for physical
qualification. The defaults for other builds are not changed.

## How the memory saving is counted

IRAM and DRAM are aliases of shared SRAM on this C3. The inventory measures
`_iram_end - _iram_start`, including alignment, and compares `_heap_start`
between matched builds. It also reports `.data` and `.bss`: moving code can
move its constants too. Do not add IRAM and aliased DRAM a second time, and do
not present a linker capacity increase as an observed free-heap measurement.

The reproducible [inventory](../tests/results/esp32c3-iram-20261001/inventory.json)
contains ELF/MAP/config SHA-256 fingerprints, every sized IRAM symbol, component
totals and functions that demonstrably moved to `.flash.text`. Missing symbols
are not automatically classified as relocated. Static symbol name collisions
are excluded from the named before/after matching.

## Candidates and dependencies

### Final linked sizes (encrypted Flash APIs retained)

| Build | IRAM text | Reserved IRAM, including alignment | DRAM `.data` | DRAM `.bss` | Extra capacity before heap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 46750 B | 47104 B (46 KiB) | 12620 B | 31368 B | — |
| Conservative (`safe`) | 43354 B | 43520 B (42.5 KiB) | 12620 B | 31368 B | **3584 B** |
| Auto Suspend (`suspend`) | 25184 B | 25600 B (25 KiB) | 10723 B | 31368 B | **23392 B** |

For Auto Suspend, the IRAM boundary saves 21504 B and the aligned data region
saves another 1888 B. `.data`'s raw reduction is 1897 B; alignment explains the
difference. Baseline/suspend `_heap_start` are `0x3fc963e0` / `0x3fc90880`.
This is a net static change with the shared RAM counted once.

### Placement candidates

| Candidate | Baseline linked IRAM | Decision / dependency |
| --- | ---: | --- |
| Ring-buffer internal helpers shared with ISR APIs | 2596 B | `RINGBUF_PLACE_ISR_FUNCTIONS_INTO_FLASH=y` moves the linked `prv*` helpers; public ordinary `xRingbuffer*` functions were already in Flash. Existing USB Serial/JTAG interrupt is allocated with flags 0, so it is masked while cache is unavailable. Re-audit if an IRAM-safe caller is added. |
| OLED I2C master ISR | 786 B | `I2C_MASTER_ISR_HANDLER_IN_IRAM=n`; `I2C_ISR_IRAM_SAFE` was already disabled. This changes placement, not the interrupt's cache-off service guarantee. |
| Posting events from IRAM ISRs | No linked IRAM contribution here | Disable `ESP_EVENT_POST_FROM_IRAM_ISR`; current app GPIO handlers use `gpio_install_isr_service(0)`. No byte saving claimed. |
| SPI Flash driver plus MSPI HAL | 9822 + 4250 B | Largest candidate. Requires working Flash Auto Suspend before `SPI_FLASH_PLACE_FUNCTIONS_IN_IRAM=n`. Keep the ROM-driver alternative off. |
| FreeRTOS ISR APIs | Component total 3724 B | `FREERTOS_PLACE_ISR_FUNCTIONS_INTO_FLASH=y` requires Auto Suspend. Essential scheduler/vector paths still remain in IRAM. |
| Timer, system, logging and ROM print wrappers | 1312 + 1476 + 546 B, with ROM wrappers in system libraries | Move using IDF's options only with Auto Suspend. These are component totals, not a promise to release every byte. |
| libc locks, abort/assert/atomics | Part of 3246 B libc total | Further candidate, not moved in this trial. Audit cache-off callers and fatal-error handling first. |
| RTC clock/time, interrupt allocation, peripheral/regi2c controls | Part of 6392 B hardware-support total | Further candidate, not moved. Clock/cache transitions and low-power paths need separate coverage. |
| GDMA / I2S interrupt path | 590 B driver plus HAL | Retained in IRAM. Small reward versus audio timing exposure. |
| PHY, vectors, cache/MMU, watchdog and low-level Flash reset | Several components | Retain. Do not blindly remove `IRAM_ATTR` or force whole archives into Flash. |
| AAC codec and application code | 0 B in linked IRAM | Already in Flash in this variant; no additional IRAM saving available here. |

Wi-Fi TX/RX optimizations, ordinary FreeRTOS and ring-buffer functions, heap
routines and lwIP fast paths are already outside IRAM in this comparison
profile. Their prior saving must not be counted again. `ESP_PHY_IRAM_OPT` is
not a useful C3 switch: the installed SDK's help says its effect is C2-only.

## Why Auto Suspend is hardware-specific

The installed IDF generic driver explicitly advertises suspend support for
manufacturer ID `0x46` (XMC-D). This board has that ID. XMC-C force-enable is
kept off. The SDK must successfully initialize suspend/resume commands; merely
building with the option does not establish hardware compatibility.

Auto Suspend lets cache reads interrupt a Flash program/erase operation. This
enables more code to execute from Flash during writes. Retain the default
50 microsecond suspend setting for this experiment. An IDF 4.3-or-newer
bootloader is required for the documented OTA enablement path; this board's
bootloader is IDF 6.0.2. Application-only OTA preserves bootloader, NVS and
SPIFFS. Test writing the inactive application slot and booting both slots.

Local authoritative implementation references (relative to ESP-IDF 6.0.2):

- `components/spi_flash/spi_flash_chip_generic.c`, `spi_flash_chip_generic_get_caps`.
- `components/spi_flash/esp_flash_spi_init.c`, `esp_flash_init_default_chip`.
- `components/spi_flash/Kconfig` and `components/spi_flash/linker.lf`.
- `components/esp_ringbuf/Kconfig`, `components/esp_driver_i2c/Kconfig`.
- `components/esp_driver_usb_serial_jtag/src/usb_serial_jtag.c` interrupt allocation.
- `components/esp_driver_dma/src/gdma.c` cache-safe channel allocation.

Public Espressif references (the online stable version can advance beyond the
locally tested SDK): [RAM usage](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/performance/ram-usage.html),
[optional Flash features](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/spi_flash/spi_flash_optional_feature.html),
[Flash concurrency constraints](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/spi_flash/spi_flash_concurrency.html).

## Reproduce

Use the same defaults, in this order, with a fresh build directory/sdkconfig:

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-iram-suspend -Sdkconfig build-iram-suspend/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.aac-ram.defaults', `
    'sdkconfig.aac-bounded-wifi.defaults','sdkconfig.cpu-profile.defaults', `
    'sdkconfig.cpu-profile-http.defaults','sdkconfig.iram-safe.defaults', `
    'sdkconfig.iram-suspend.defaults')
```

Omit the last defaults file for the conservative placement trial (`safe` is a
short build label, not a safety certification); omit both `iram-*` defaults for
the matched baseline. Previously generated sdkconfig values override defaults:
use a fresh configuration when reproducing.

Run the inventory with ESP-IDF's Python:

```powershell
python tools/esp32c3_tests/iram_inventory.py `
  --build baseline=idf/esp32c3-oled-native/build-iram-baseline `
  --build safe=idf/esp32c3-oled-native/build-iram-safe `
  --build suspend=idf/esp32c3-oled-native/build-iram-suspend `
  --output tests/results/esp32c3-iram-20261001/inventory.json
```

Physical test commands and outcomes are recorded below.
The preliminary `initial-unencrypted-inventory.json` retained an additional
API-removal experiment. It is superseded: final profiles retain encrypted
Flash read/write APIs and must use the final inventory for byte counts.

## Physical memory and CPU comparison

The baseline and Auto Suspend image each ran the same LC → HE → HEv2 sequence,
35 seconds per continuous fixture, with the same saved 10-block input buffer.
The baseline reproduced its pre-existing SBR allocation failure: 55128 B was
requested while the largest block was 53248 B. The candidate ran full SBR/PS.
No decoding arithmetic or allocation sizes were changed.

At `app-start`, free heap increased **288000 → 311392 B**, exactly **23392 B**.
The largest block increased **147456 → 172032 B**. These are distinct metrics:
the largest-block increase includes allocator geometry and is not an additional
saving to add to the free-heap difference.

| Input | Baseline result; total / decode CPU | Auto Suspend result; total / decode CPU | Candidate minimum sampled free / largest |
| --- | --- | --- | ---: |
| AAC-LC 48 kHz stereo | PASS; 36.583% / 18.583% | PASS; 37.933% / 19.017% | 99068 / 65536 B |
| HE-AAC 48 kHz stereo | FAIL, core-only; CPU not comparable | PASS; 52.083% / 36.433% | 42672 / 10752 B |
| HE-AAC v2 44.1 kHz stereo | FAIL, core-only; CPU not comparable | PASS; 56.667% / 41.200% | 42972 / 10752 B |

CPU numbers are task-runtime means 5–35 seconds after the first PCM checkpoint.
LC total CPU increased by 1.350 percentage points and decoder-task CPU by 0.434
points in this pair. Do not call that zero overhead or a precise cache penalty:
there is only one pair, with Wi-Fi traffic and scheduling variability. The
baseline's failed HE output does less work and is not a full-HE speed control.
The candidate's minimum-ever heap reached 18972 B during this sequence. Minimum
observed decoder stack headroom was 14368 B; output-task headroom was 1220 B.

After the first OTA, a memory-run setup attempt timed out on `board.info()`
before tests started. Passive serial still showed ongoing decoding; three
subsequent HTTP identity requests succeeded. Both the failed attempt and those
diagnostics are retained. Its cause is not isolated, so it must not disappear
from the qualification report as a clean pass. The subsequent full survey
completed and verified settings, Wi-Fi file and playlist preservation.

The USB capture did not retain the SDK's early suspend-init message. The tested
image/config identity, successful initialization and actual OTA write tests are
separate evidence; this audit does not claim a direct suspend-register trace.

Reproduce after installing the selected saved image via WebUI OTA:

```powershell
python tools/esp32c3_tests/memory.py --board http://BOARD_IP --host PC_LAN_IP `
  --serial-port COM9 --output .build/iram-memory
python tools/esp32c3_tests/summarize_memory.py --input .build/iram-memory `
  --output .build/iram-memory/summary.json
```

Raw measurements: [baseline](../tests/results/esp32c3-iram-20261001/hardware/baseline-memory/report.json),
[Auto Suspend](../tests/results/esp32c3-iram-20261001/hardware/suspend-memory/report.json),
with `status.json`, `performance.json` and `summary.json` beside each report.

## Mixed-codec and OTA qualification

The Auto Suspend [mixed matrix](../tests/results/esp32c3-iram-20261001/hardware/suspend-matrix/report.json)
records **17 PASS and 3 FAIL cases**. The failed switching case contains two
failed station changes; it is not three additional decoder failures.

- MP3 320 kbit/s, Vorbis q10, Opus 510 kbit/s, AAC-LC 48 kHz, HE-AAC 48 kHz
  and HE-AAC v2 44.1 kHz pass both auto-detect and explicit-codec finite-file
  playback/EOF checks.
- FLAC level 8, 48 kHz stereo produces the correct PCM layout, but both file
  trials fail to reach EOF within the observation window.
- Of 21 station changes, 19 meet the strict sampled-playback gate. All six
  HE/v2 changes pass at full rates. Two FLAC starts provide too few samples
  in seven seconds. The largest HTTP request delay in those FLAC observations
  is 4360 ms. This is a failed acceptance result even though audio is reported.
- WebSocket format/reconnect and three software reboot/readiness checks pass.
  Candidate readiness is 5.422–6.250 s versus 5.438–6.594 s in the baseline;
  these small samples do not establish an isolated Wi-Fi connection-time gain.
- No allocation-failure, heap-corruption or panic marker appears in the
  captured matrix log. Idle heap checkpoints are 167872–168228 B, largest
  block 114688 B; there is no downward trend across these three cycles.

During the slow FLAC file observations, the CPU is mostly idle (about 81–89%),
while each decoder call window consumes about 21–24% of the duration of the PCM
it actually generates. Only 0.38–0.67 seconds of audio is produced per five
wall-clock seconds. This points to waiting outside active decoding, not CPU
saturation by the FLAC math. Network/scheduling causality is not established.
RSSI ranges from approximately -76 to -68 dBm; do not attribute RSSI changes
to the Flash interface or code placement from this observation.

**OTA initiated during verified AAC playback passes from the Auto Suspend
image to the matched baseline**, including writing the other slot, booting
its exact image hash and comparing settings, Wi-Fi file and playlist. Upload
through successful reboot takes 86.938 s. This directly exercises Flash writes
while the running image's Flash driver/system code resides in Flash. It is
not an IRQ-latency, encrypted-partition or power-cut-recovery test.

Use the retained transition runner for a different-image test (both images
must have their exact sdkconfig alongside them):

```powershell
python tools/esp32c3_tests/ota_transition.py --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 `
  --current-firmware firmware/development/esp32c3-iram-suspend/app.bin `
  --firmware firmware/development/esp32c3-iram-baseline/app.bin `
  --output .build/iram-ota-transition
```

It verifies the initial image, starts the fixture, leaves the firmware to stop
playback for OTA, verifies the destination image/slot and keeps private settings
in RAM only. [Retained result](../tests/results/esp32c3-iram-20261001/hardware/suspend-to-baseline-ota/report.json).

### FLAC control and promotion decision

The matched baseline was installed again and ran MP3/FLAC with both codec
selection modes, followed by three MP3 → FLAC cycles. Both FLAC EOF checks
**also fail on the baseline**. Its FLAC decode windows similarly generate only
0.38–0.58 seconds of PCM per five seconds, with roughly 21–24% decoder work per
PCM duration. Baseline HTTP latency reaches 4985 ms. The EOF/throughput problem
therefore exists without the new IRAM placement; it is not established as an
Auto Suspend regression.

However, this shorter baseline switching sequence passes all six changes,
whereas the seven-codec candidate sequence had two failed FLAC sampling gates.
The sequences and RF conditions differ, so this does **not** prove unchanged
switching latency. Keep that unresolved difference and the initial candidate
HTTP timeout as qualification gaps, rather than declaring complete equivalence.
[Control evidence](../tests/results/esp32c3-iram-20261001/hardware/baseline-flac/report.json).

**No production defaults are promoted.** The conservative profile is build-only;
the larger profile demonstrates real DRAM headroom, full-rate AAC switching and
working OTA on this XMC-D board, but is still an explicit experiment. The original
uninstrumented bounded-Wi-Fi image is restored after testing, with its exact ELF
identity and settings preservation recorded in `hardware/restore-ota.json`.

Before promotion, isolate the FLAC/network delay with identical repeated A/B
sequences; repeat CPU timing; qualify IRQ latency and audible continuity during
Flash writes, and the relevant AP, OLED/control, deep-sleep and HTTPS modes.
Those checks were not performed by the runs above. No claim of universal Flash
chip support, unchanged worst-case interrupt latency or complete feature
qualification follows from a larger heap or a passing OTA alone.

Saved images and exact configurations are under
`firmware/development/esp32c3-iram-{baseline,safe,suspend}/`. Validate the retained
measurements, feature-preserving configuration differences, failure records and
OTA restoration with:

```powershell
python tests/test-esp32c3-iram.py
```

The later [Wi-Fi buffer balance experiment](ESP32C3_WIFI_BUFFER_BALANCE_20261001.md)
uses the same IRAM layout with dynamic RX/TX limits of 16. It investigates the
unfinished FLAC transfers above and records a separate image, test outcomes and
final board state; it does not rewrite this six-buffer audit's failures.
