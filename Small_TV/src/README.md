# Modular Small TV ESP32-C2 reconstruction

This directory contains a standalone ESP-IDF application reconstructed from
our factory-firmware decompilation. It builds a real ESP32-C2 application,
bootloader and partition table. It is a source-level reconstruction, not a
byte-identical rebuild of the manufacturer's unavailable source.

The successful build is archived in
[`firmware/development/small-tv-esp32c2-reconstructed`](../../firmware/development/small-tv-esp32c2-reconstructed).
Compilation and host tests are verified; boot, panel orientation, brightness,
Wi-Fi/SNTP/HTTPS and runtime heap/stack use still require a physical board test.
This work did not flash or reset the device. OTA is deliberately absent.

## Source organization and names

| Directory | Responsibility |
|---|---|
| `app/app_main.c` | Initialization and task startup |
| `app/settings/` | Versioned NVS settings, validation, RGB565 conversions |
| `app/display/` | ST7789 hardware SPI, LEDC backlight, four clock themes |
| `app/media/` | Flash assets, streaming JPEG/BMP, validated photo uploads |
| `app/network/` | Station/AP mode, real Wi-Fi scan, bounded captive DNS |
| `app/services/` | SNTP, timezone selection, HTTPS weather and cached results |
| `app/web/` | Recovered HTTP contracts, pages, settings and photo APIs |
| `third_party/` | Pinned cJSON, TJpgDec and licensed Spleen font |
| `reference/` | 176 exported functions split into 16 logical pseudocode modules |

[`symbol-map.json`](symbol-map.json) preserves every exported function's
original address and name, inferred logical name, category and corresponding
native module. It also names 43 globals and 133 local/parameter aliases from observed settings/API/rendering
uses. For example, `FUN_ram_4200c74e` becomes `captive_dns_task_at_4200c74e`,
and `DAT_ram_3fcb7d1c` becomes `day_backlight_per_mille_at_3fcb7d1c`.

`reference/*.c` is **Ghidra pseudocode, excluded from compilation**. Unknown
SDK calls, overlapping globals and unproven local types retain their address
or decompiler aliases. Guessing an attractive name is not evidence of its
meaning. The executable files in `app/` use real C types and descriptive
functions, configuration fields, buffers and state variables. SDK code is
provided by ESP-IDF rather than stubbed out or mapped to old machine addresses.

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
rebuilds the custom animation headers, generates the font and embeds the
recovered UTF-8 HTML. It never reads the private settings or the original
full-flash dump. Generated data stays in the ignored `.build/` directory.

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
credentials. Failed station connections make the setup AP available after
20 seconds, with retries continuing. Configuration changes persist in a new
NVS namespace; they do not migrate the manufacturer's raw settings sector.
Restart requests wait for persistence and a response opportunity.

`/advanced` configures the NTP server, the owner's OpenWeatherMap key and
the night brightness schedule. The factory's embedded weather key is not
copied into these sources. Weather requests use certificate-verified HTTPS
after SNTP has established a usable date; updates run every 30 minutes and
after city/key changes. The recovered 109-entry country/POSIX-TZ table is
used initially. A weather result for the current city supplies its UTC
offset, refreshed at each successful request.

Four themes render a classic digital clock/weather view, simple digital
clock, photo slideshow and analog dial. Five animations contain 98 frames;
five photos, 18 weather icons and four status images are packed. The
native layouts and Spleen ASCII font approximate the original graphics;
they do not reproduce the original font tables, non-ASCII glyphs or slideshow
fade sequence. The status images remain available as assets, while the new
weather view renders its values with text.

The `timeSync` compatibility flag is stored as in the recovered handler:
the original page supplies no browser timestamp. Time is synchronized by
SNTP. `clickCount` is stored for API compatibility; the advanced page is
directly accessible. The original UI's Celsius label contradicted its
`tempUnit=1` Fahrenheit implementation; the embedded firmware copy corrects
the label. Local-site and archived source HTML files are unchanged.

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

```powershell
& .\Small_TV\src\tests\run.ps1
```

The test runner compiles the actual settings, media, upload, HTTP and DNS
packet C sources with MSVC. Its platform adapter supplies in-memory flash,
NVS and HTTP I/O; these are host-test dependencies, not production stubs.
It exercises all 107 JPEGs, all 98 animation frames, 18 BMPs, settings and
RGB565 conversion, complete/partial/duplicate/out-of-order uploads, privacy
metadata, multipart binary data, bad request values, source-origin checks,
route registration and malformed/truncated DNS. The result is recorded in
[`validation.json`](validation.json).

ESP32-C2 compilation/linking and esptool image validation cover the real
SDK calls and target format. Host tests do not establish hardware operation,
Wi-Fi/TLS behavior, electrical polarity or adequate runtime heap/stack headroom.

TJpgDec is vendored from
[Espressif's esp_jpeg component](https://github.com/espressif/idf-extra-components/tree/43de626f617b2a18a67f12bf09e68223df9fef9a/esp_jpeg).
ESP32-C2 uses the software decoder. ChaN's copyright/redistribution terms,
cJSON's MIT license and Spleen's BSD-2-Clause license are retained in
`third_party/`. TJpgDec's configuration and Windows fixed-width-type includes
are adapted for this project; its decoding algorithm is unchanged.
