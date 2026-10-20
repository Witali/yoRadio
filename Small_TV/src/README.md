# Modular Small TV ESP32-C2 reconstruction

This directory contains a standalone ESP-IDF application reconstructed from
our factory-firmware decompilation. It builds a real ESP32-C2 application,
bootloader and partition table. It is a source-level reconstruction, not a
byte-identical rebuild of the manufacturer's unavailable source.

The successful build is archived in
[`firmware/development/small-tv-esp32c2-reconstructed`](../../firmware/development/small-tv-esp32c2-reconstructed).
Compilation and host tests are verified; boot, panel orientation, brightness,
Wi-Fi/SNTP/Internet weather and runtime heap/stack use still require a physical board test.
This work did not flash or reset the device. OTA is deliberately absent.

The earlier archived application passed QEMU ESP32-C2 boot, LCD,
animation, Wi-Fi association, DHCP, UDP NTP and reset tests. Current scene
comparisons are recorded separately in [the parity checkpoint](../qemu/parity/README.md).
Full behavioral identity is still work in progress. The emulator seeds
synthetic settings in a working flash copy and provides an isolated time server
using host UTC. [Screens and reports](../qemu/README.md) document the result and
virtual-time limitations; physical-board and Internet weather checks remain pending.

## Source organization and names

| Directory | Responsibility |
|---|---|
| `app/app_main.c` | Initialization and task startup |
| `app/settings/` | Factory raw-sector compatibility, NVS migration, validation and RGB565 |
| `app/display/` | ST7789 hardware SPI, LEDC backlight, four clock themes |
| `app/media/` | Flash assets, streaming JPEG/BMP, validated photo uploads |
| `app/network/` | Station/AP mode, real Wi-Fi scan, bounded captive DNS |
| `app/services/` | SNTP, factory timezone selection, HTTP/Kelvin weather and cached results |
| `app/text/` | Strict UTF-8 scalar decoding and complete label prefixes |
| `app/web/` | Recovered HTTP contracts, pages, settings and photo APIs |
| `codec/` | Bounded JPEG API, memory/backing adapters and coefficient conversion; UI integration pending |
| `storage/` | Guarded NOR transport, scratch files, atomic journal and verified frame cache |
| `third_party/` | Pinned cJSON, TJpgDec, offline libjpeg-turbo source bundle and licensed Spleen font |
| `reference/` | 176 exported functions split into 16 logical pseudocode modules |

[`symbol-map.json`](symbol-map.json) preserves every exported function's
original address and name, inferred logical name, category and corresponding
native module. It also names 44 globals and 133 local/parameter aliases from observed settings/API/rendering
uses. For example, `FUN_ram_4200c74e` becomes `captive_dns_task_at_4200c74e`,
and `DAT_ram_3fcb7d1c` becomes `day_backlight_per_mille_at_3fcb7d1c`.

`reference/*.c` is **Ghidra pseudocode, excluded from compilation**. Unknown
SDK calls, overlapping globals and unproven local types retain their address
or decompiler aliases. Guessing an attractive name is not evidence of its
meaning. The executable files in `app/` use real C types and descriptive
functions, configuration fields, buffers and state variables. SDK code is
provided by ESP-IDF rather than stubbed out or mapped to old machine addresses.

All 162 production C functions have an entry comment explaining their purpose.
Corrected functions also carry searchable entry-comment markers:
`FIXED_FACTORY` identifies a deliberate correction of an original firmware bug;
`FIXED_RECONSTRUCTION` identifies a repair of our C implementation to restore
factory behavior. `REQUESTED_CHANGE` identifies an explicit user requirement,
such as photo privacy, rather than evidence of a factory bug. Each marker states
the reason and cites the original address when established. SDK replacement and
unverified hypotheses are not classified as confirmed factory corrections.
The [correction marker convention](CORRECTION_MARKERS.md) documents their usage,
examples and the functions already marked.
The [working context](WORKING_NOTES.md) preserves the current recommendations
and next checks; the [work journal](WORK_LOG.md) records findings and validation.
Classic city, description and weather-title text is clipped to its own field.
Long strings scroll left and back with pauses; short strings remain centered.
Status refreshes preserve the phase; changed text or theme re-entry resets it.
Missing/failed weather icons and shortened labels clear their complete regions.
[Weather/scroll checks](../qemu/parity/weather-checks.md) distinguish confirmed
factory fixes from this requested scrolling extension.
[Calendar checks](../qemu/parity/calendar-checks.md) cover year/day-number jumps
at unchanged local time and clean replacement of centered simple-clock dates.
[Regional settings checks](../qemu/parity/regional-settings-checks.md) restore
the original 20-byte country/region field through HTTP, raw-sector storage,
weather and time workers. All 109 keys pass host API/storage tests; all 15
regional keys have real QEMU transport/calendar checks. Native NVS version 2
uses 364 bytes and migrates the original 344-byte version 1 without changing
the manufacturer's raw-sector ABI. Actual SDK NVS migration and fallback boots
are tested separately from the timezone calculation.
[JPEG checks](../qemu/parity/jpeg-checks.md) execute both real decoders for all
107 public images, restore byte-clipped IDCT colors and verify bounded cleanup
after streaming errors, retries, validation and clipped placement.
Comments also explain byte-padded/LSB-first fonts, fixed raw-sector offsets,
timer thresholds, photo fades, MIME binary parsing and DNS packet bounds.
Where machine instructions were checked directly, comments cite their original
addresses. [Assembly audit](reference/assembly/README.md) separates those checks
from inference based on the Ghidra export.
`tools/assist_c_port.py` produces JSON and Markdown review reports from decoded
objdump text: basic blocks, natural loops, calls, stack-frame hints and signed/
unsigned C branch conditions. It can apply the logical names and C-module paths
from `symbol-map.json`. Gaps, indirect transfers and outgoing branches stay visible
for manual review. The tool reports control-flow facts; instruction bodies and
external calls still need a C implementation and behavior comparison. See the
[command examples and tests](reference/assembly/README.md#control-flow-review-tool).

The broader export used for organization came from the existing analyzed
factory ELF, including application functions and SDK callers. Its SHA-256
and the immutable flash-dump SHA-256 are recorded in the symbol map. To
intentionally reorganize a new export:

```powershell
python Small_TV/src/tools/organize_decompilation.py path/to/ghidra-export.c
```

## Build

From the repository root on this Windows workspace:

```powershell
& .\Small_TV\src\build.ps1
```

The default is `DEBUG=OFF`: application, ESP-IDF and bootloader logs are limited
to warnings and errors. Info/debug/verbose source logging is excluded by the SDK
maximum level. The immutable ROM boot message is independent of this setting.
For diagnostic logging, use:

```powershell
& .\Small_TV\src\build.ps1 -DebugLogging
```

This passes `-DDEBUG=ON` to CMake and selects the SDK debug level. With plain
`idf.py`, add `-DDEBUG=ON` or `-DDEBUG=OFF` before `build`. This changes logging,
not optimization, assertions or GDB symbols. Reusing an explicit build directory
works in both directions; the wrapper always passes a mode rather than retaining
the previous CMake cache value. PowerShell's common `-Debug` parameter controls
PowerShell itself; the firmware switch is `-DebugLogging`.

Default debug builds use `.build/small-tv-esp32c2-debug` and are archived under
`firmware/development/small-tv-esp32c2-reconstructed-debug/`. Ordinary builds keep
the original directories. Each archive manifest records `debug_logging`, so a
diagnostic build cannot silently replace the ordinary hand-off image.

QEMU has a separate `-DebugLogging` build switch for its packet/DNS/NTP traces.
The existing transport parity tests that explicitly assert those diagnostic
events need a diagnostic QEMU binary; ordinary HTTP, DMA, LCD and SNTP behavior
must also be exercised with the release binary. A missing disabled log message
is not evidence of a firmware failure. See QEMU's Small TV README and the
[scoped logging checks](../qemu/parity/debug-logging-checks-20261017.md).

The script uses the already installed ESP-IDF v6.1 development checkout
`.idf/v6.1-9a97f6c54ec6`, pinned to commit
`9a97f6c54ec638111ce55cd36581b3c192f15207`, and tools in `.idf/tools-v6.1`.
The original firmware used v5.5.4; this reconstruction uses the installed,
fully initialized v6.1 toolchain. `-DependencyRoot` and `-BuildDirectory`
override the local paths. Git, PowerShell 7 and Python 3.12 are required.

For a fresh environment, check out that exact revision from
[Espressif's ESP-IDF repository](https://github.com/espressif/esp-idf), initialize
its submodules and install its ESP32-C2 tools/Python environment with the SDK's
`tools/idf_tools.py install --targets esp32c2` and `install-python-env` commands.
Set `IDF_TOOLS_PATH` to `.idf/tools-v6.1` during installation. The Windows
wrapper expects the repository's bootstrap Python at
`.idf/python-3.12.10/tools/python.exe`; an ordinary exported ESP-IDF environment
can also build with the commands below. No component-manager downloads occur
during this project's build.

```text
python Small_TV/src/tools/prepare_resources.py --output .build/small-tv-esp32c2/resources
cd Small_TV/src
idf.py -B ../../.build/small-tv-esp32c2 --no-ccache -D SDKCONFIG=../../.build/small-tv-esp32c2/sdkconfig -D SDKCONFIG_DEFAULTS=sdkconfig.defaults build
```

Resource preparation uses only the Python standard library. It repacks the
sanitized extracted JPEGs, reconstructs BMP weather icons from PNG pixels,
rebuilds the custom animation headers, embeds the extracted factory font tables and the
recovered UTF-8 HTML. It never reads the private settings or the original
full-flash dump. Generated data stays in the ignored `.build/` directory.
The one-time `tools/extract_factory_bitmaps.py` extractor verifies the dump hash
and copies only the identified public drawing tables into `resources/factory/`.
Ordinary builds use those checked-in tables and verify their manifest hashes.

`build.ps1` saves `app.bin`, `bootloader.bin`, `partition-table.bin`,
`assets.bin`, actual `sdkconfig`, image hashes, asset hashes and a manifest
of compiled source/generated-resource hashes in the development archive.
Running plain `idf.py` requires copying successful hand-off artifacts there
as required by the repository rules. The wrapper only builds and archives;
it has no flash operation.

## Hardware and memory

- ESP32-C2 / ESP8684H, 120 MHz, **26 MHz crystal**, 4 MiB flash, DIO at 30 MHz.
- SPI2, mode 3, requested panel clock 40 MHz, DMA, no MISO or CS GPIO.
- GPIO4 SCK, GPIO6 MOSI, GPIO5 D/C, GPIO1 reset, GPIO18 backlight.
- ST7789-family 240×240 panel, RGB565, MADCTL `0x00`, inversion enabled.
- LEDC channel/timer 0: 1 kHz, 13-bit duty. The recovered UI mapping is
  `duty_per_mille = 1000 - percentage * 10`, with no LEDC output inversion.
- Streaming rendering: 1920-byte SPI transfer buffer and 8192-byte JPEG work
  pool. There is no 115,200-byte full-screen framebuffer or 100 KiB upload
  buffer. JPEG work is allocated only during decoding.

| Flash region | Offset | Allocated bytes |
|---|---:|---:|
| Bootloader and table area | `0x000000` | 36,864 |
| NVS | `0x009000` | 24,576 |
| PHY area | `0x00f000` | 4,096 |
| Factory application | `0x010000` | 1,536,000 |
| Unallocated gap | `0x187000` | 495,616 |
| Media partition | `0x200000` | 1,994,752 |
| Unallocated tail / original settings sector | `0x3e7000` | 102,400 |
| **Total** | | **4,194,304** |

The application image uses approximately 1 MiB of its 1.465 MiB partition;
the exact size is in the build manifest. The media partition includes the
five 100 KiB photo slots, five 200 KiB animation slots, weather/status slots
and their unused padding. About 1 MiB is spare application capacity plus
the gap/tail, not a missing three megabytes. Keeping original absolute media
offsets makes comparison with the dump straightforward. No SPIFFS/LittleFS
filesystem or second OTA application partition is created.

If manually installing the archived images later, their offsets are
`bootloader.bin` → `0x0`, `partition-table.bin` → `0x8000`, `app.bin` →
`0x10000`, and **`assets.bin` → `0x200000`**. Plain `idf.py flash` does not
include the separately packed media, so it alone is insufficient for a fresh
installation. Board installation was not performed as part of this task.

## Restored behavior and deliberate differences

The native program implements all 34 recovered method/URI pairs listed in
[`registered-routes.tsv`](../analysis/security/registered-routes.tsv), plus
`/setup`, `/settings`, HTML page aliases and `/advanced`.

At first start, join the open `Small_TV` access point and open
`http://192.168.43.1/`. The setup page scans real networks and saves station
credentials. After four failed station retries, the program saves factory Wi-Fi
mode 2 and restarts into setup. A pending association or DHCP lease retains
station mode; the independent 18.1-second display animation is not a network
failure deadline. A successful lease clears an earlier failed-attempt latch.
An existing mode-2 sector enters setup even when it retains an SSID. The original
444-byte sector at `0x3e7000` takes precedence over the earlier native NVS blob;
settings changes update both formats. Current NVS v2 uses 364 bytes and imports
the prior 344-byte v1 layout. Restart requests wait for persistence and a response
opportunity. No original settings, credentials or keys are embedded in sources.

`/advanced` configures the NTP server, the owner's OpenWeatherMap key and
the night brightness schedule. The factory's embedded weather key is not
copied into these sources. Weather follows the original HTTP endpoint with
Kelvin values: Celsius truncates toward zero before Fahrenheit conversion;
min/max retain double precision. Text is limited to 15 bytes and wind bearings
use the original sixteen sectors and literal hyphenated direction labels.
The QEMU weather fixture verifies real DNS/TCP/HTTP, cache values and four LCD
regions for positive/negative responses; HTTP 503 JSON is rejected despite the
factory parser accepting it. The recovered 109 country keys retain their generic
timezone defaults; [pinned IANA rules](resources/timezones/README.md) correct the
factory's implicit DST strings and outdated offsets. The weather UTC offset
does not replace this selection. [Timezone checks](../qemu/parity/timezone-checks.md)
execute actual RV32 code and Newlib against independent TZif conversion. Requests retry
after about 3.1 seconds and successful updates repeat after 1801 timer seconds
(about 1981.1 real seconds at the recovered 11-tick cadence).

Four themes render a classic digital clock/weather view, simple digital
clock, photo slideshow and analog dial. Five animations contain 98 frames;
five photos, 18 weather icons and four status images are packed. The
renderer now uses the original 16/24/32/40/64/80-pixel bitmap tables, unit symbols,
clock plates, coordinates, colors, unpadded date, blinking colon and transparent
IP footer. Classic animation is at `(160,160)`; photos occupy the full screen.
The slideshow applies duty levels `300,600,1000,600,300,0`, changing the photo
at duty 1000. Digital fields and analog hands update incrementally, following
the recovered dispatch flags. Analog stroke offsets round rather than truncate.
The simple clock corrects the confirmed Sunday bug: standard `tm_wday == 0`
displays `Sun` instead of repeating the date in green. Factory weekday 7 still
maps to Sunday for compatibility. At the user's explicit request, confirmed
vendor bugs are corrected rather than reproduced; verification records these
intentional differences separately from incomplete reconstruction.
Analog strokes retain the correct perpendicular `cos/sin` offset pair, fixing
the vendor's swapped pair that makes axis-aligned thick strokes collapse.
The simple theme follows real hour/minute changes, correcting the factory's
stale digits caused by its 66-second update flag. Colon events remain independent.
Setup text and the `Ver:0.0.2` progress screen are restored. The earlier extra
seconds/IP overlay and clock-on-photo strip are removed. Factory ASCII and
temperature-unit bitmaps are retained. UTF-8 text uses 452 non-ASCII glyphs from
the bundled Spleen font, scaled to the original 16/24/32-pixel cells. Unsupported
Unicode scalars render one `?`; malformed bytes cannot consume the following
ASCII character. This is a limited bitmap font, without shaping or bidirectional
layout. Weather labels retain their original 15-byte source budget but stop at
a complete UTF-8 boundary. Width, centering and scrolling count glyphs rather
than bytes. UTF-8 city bytes are percent-encoded in weather URLs, and a failed
HTTP-client initialization is checked before use. The factory's unguarded
client call can crash on such a city. [Text checks](../qemu/parity/text-checks.md)
record the literal errors separately from corrected behavior.

The `timeSync` compatibility flag is stored as in the recovered handler:
the original page supplies no browser timestamp. Time is synchronized by
SNTP. `clickCount` is stored for API compatibility; the advanced page is
directly accessible. The working pages correct the original opposite Celsius
and mile captions: `tempUnit=1` means Fahrenheit, `mileDisplay=1` means km/h.
Brightness covers 0..100%, and the unsupported browser-time control is disabled.
Switches become editable only after valid settings load; six HTTP sessions
support the settings page's parallel requests. `/advanced` remains an extra
directly accessible page for the owner's NTP/weather configuration.

The photo page now offers a square selection that can be moved by dragging
inside it and resized by dragging any corner, with zoom and position sliders.
Browser Canvas resamples the chosen region to 240×240 JPEG, and
JavaScript strips APP/COM metadata before sending chunks to the board.
Cancel/Escape sends no upload and preserves the slot. Native JPEG dimensions,
baseline/scan completeness and privacy validation still apply. Original HTML
bytes remain preserved under `../local_site/source/`.

The reconstruction corrects unsafe DNS bounds, image-buffer overlap,
unbounded/misordered chunks, the `/wifireset` credential-copy defect, and
the panel's inclusive end-coordinate literal of 240 (now 239). Photo uploads
use ordered 4096-byte chunks, idempotent last-block retries, a 100 KiB slot
limit and a 120-second abandoned-session timeout. A partial slot is marked
absent in NVS before erase. Finish validates a complete baseline 240×240 JPEG
and rejects EXIF, other private metadata, progressive images and appended
data. All stock JPEGs are the already sanitized exports. DNS replies fit a
bounded packet and only serve peers on the setup AP subnet. Cross-origin
browser writes are rejected. Local HTTP management and the setup AP retain
the original unauthenticated access model.

## Validation

The [functional test suite](tests/README.md) adds a single `tests/run-all.ps1`
entry point, coverage of all 40 registered HTTP contracts, production Wi-Fi/
weather/SNTP/clock-task execution with deterministic ESP-IDF adapters, LCD SPI
protocol and backlight sweeps, archived-image integrity checks, and full-firmware
QEMU boot/reset/SNTP/scene tests. Its report distinguishes passed, failed and
unexecuted groups. Physical-board/browser/soak acceptance scenarios are documented
separately and are not reported as passing automated tests.

QEMU now also checks real localhost HTTP setup, Wi-Fi scan, saved credentials,
AP-to-STA reboot and persistence. Setup uses an idle STA alongside the AP because
ESP-IDF cannot scan in AP-only mode; it does not connect without saved credentials.
This matches the factory APSTA initialization at `0x4200d06e`. The factory's
zero-result `/scan` null dereference and literal `/configure` JSON parser are
documented in the [network test scope](../qemu/README.md).

The [machine-level renderer checks](../qemu/parity/machine-checks.md) execute
the immutable factory instructions and the actual compiled C ELF in RV32
Unicorn. They compare every framebuffer pixel for controlled simple/analog
clock inputs and preserve framebuffer history across updates. The Sunday and
analog-stroke fixes have explicit, separately tested reference paths; no region
is masked.
The [classic checks](../qemu/parity/classic-checks.md) add exact field pixels and
media-call identities for 261 cases, plus 1,545 executed animation transitions.
The GIF cursor now follows the factory terminator rule and survives selection
and theme changes. Partially visible glyphs are clipped instead of dropped;
the literal 17-pixel difference for the last letter of Thunderstorm is retained
as a confirmed factory correction and checked against the original bitmap.
These classic checks record media requests rather than decoding image pixels.
These checks supplement the whole-board QEMU captures and do not establish
network, service scheduling or hardware equivalence.

[Control checks](../qemu/parity/control-checks.md) compare 79,296 timer ticks,
13,440 slideshow transitions and 60 frames with independent second/minute flags
against executed factory instructions. Hardware GPTimer now starts before
network initialization. Its ISR only updates counters/flags; one task owns SPI.
Events coalesce across blocking HTTP/upload work. Weather retries count completed
main-loop iterations and periodic requests use the global timer flag, instead
of a worker deadline measured from its last response. Photo rotation preserves
next-slot/fade state and restores configured day/night brightness after a fade,
correcting the vendor's full-brightness override in photo mode.
The control gate also compares 144,246 executed LEDC calls/decisions. Backlight
initialization follows zero-duty channel setup with explicit set/update, and
scheduled brightness skips unchanged levels. The common setter tracks the
actually applied level, preserving configured brightness after photo fades.

```powershell
& .\Small_TV\src\tests\run.ps1
& .\Small_TV\src\tests\run-machine-oracle.ps1
& .\Small_TV\src\tests\run-machine-oracle.ps1 -Control
```

The test runner compiles the actual settings, Kelvin weather parser, media, upload, HTTP and DNS
packet C sources with MSVC. Its platform adapter supplies in-memory flash,
NVS and HTTP I/O; these are host-test dependencies, not production stubs.
It exercises all 107 JPEGs, all 98 animation frames, 18 BMPs, settings and
RGB565 conversion, complete/partial/duplicate/out-of-order uploads, privacy
metadata, multipart binary data, bad request values, source-origin checks,
route registration, factory-sector/NVS migration, explicit Wi-Fi mode, negative
temperature truncation and malformed/truncated DNS. The result is recorded in
[`validation.json`](validation.json).

ESP32-C2 compilation/linking and esptool image validation cover the real
SDK calls and target format. Host tests do not establish hardware operation,
Wi-Fi/Internet behavior, electrical polarity or adequate runtime heap/stack headroom.

[Current QEMU comparison](../qemu/parity/README.md) keeps actual SPI framebuffer
captures and measured differences for setup and all four themes. It does not
constitute a proof that every path of every SDK/application function is identical.

TJpgDec is vendored from
[Espressif's esp_jpeg component](https://github.com/espressif/idf-extra-components/tree/43de626f617b2a18a67f12bf09e68223df9fef9a/esp_jpeg).
ESP32-C2 uses the software decoder. ChaN's copyright/redistribution terms,
cJSON's MIT license and Spleen's BSD-2-Clause license are retained in
`third_party/`. TJpgDec's configuration and Windows fixed-width-type includes
are adapted for this project. Baseline header checks reject invalid quantization
table IDs, unsupported sample precision, inconsistent frame component lengths
and oversubscribed Huffman trees;
the IDCT, color conversion and output algorithms are unchanged.
