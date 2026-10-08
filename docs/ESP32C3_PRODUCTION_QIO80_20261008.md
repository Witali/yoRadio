# Requested ESP32-C3 production build with QIO 80 MHz

## Configuration

Following the [DIO/QIO comparison](ESP32C3_QIO80_RECHECK_20261008.md), the user
requested a quiet production build from `codex/esp32c3-idf-upgrade` with QIO
enabled. This selects QIO for this saved variant; the repository's generic
board default remains DIO. The earlier physical failures remain in their report.

The build uses `build-production.ps1`, the normal board/production defaults and
a fresh sdkconfig seeded from `sdkconfig.qio80.defaults`. The reproducible recipe
is retained with the deployment evidence. ESP-IDF is pinned to revision
`9a97f6c54ec638111ce55cd36581b3c192f15207` of the 6.1 series.

- Flash: **QIO 80 MHz**, 4 MiB; CPU: 160 MHz.
- Deep sleep: off; internal RTC source; no external crystal required.
- Console, firmware/bootloader logs and CPU/DMA profiling: off.
- Flash boot probe and CLZ benchmark: off; no `app_main` wrapper in the ELF.
- Compact PC19 AAC with full SBR/PS and output rates/channels retained.
- Output task has priority over decoding; the tick remains 1 ms.
- Normal static TLS buffers, full 16 KiB receive record and standard CA bundle.
- Auto Suspend, adaptive-input/TLS reservation and experimental placement
  overlays are not enabled by this production recipe.

This configuration differs from the laboratory memory/profile configuration.
Its deployment smoke checks do not replace the laboratory acceptance tests or
establish that the HEv2 heap behavior has been fixed.

## Saved files and provenance

Variant directory:
[`firmware/development/esp32c3-idf-6.1-r9a97-production-qio80/`](../firmware/development/esp32c3-idf-6.1-r9a97-production-qio80/)

| Field | Value |
| --- | --- |
| Project version | `idf61-qio80-8c1f2d2d` |
| Source HEAD at build | `8c1f2d2d` |
| Application bytes | 1,446,688 |
| Application SHA-256 | `21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a` |
| ELF SHA-256 | `54ec71b493261f3c00f86a649625c83e8c772b00eb2af5a3aae594c25e937094` |
| IRAM text | 54,574 bytes |
| DRAM data / BSS | 12,396 / 27,696 bytes |

The manifest also records the matching bootloader/configuration hashes and
the two local source overlays. One is the new QIO config; the other is an
inactive CLZ benchmark block in the local main CMake file. Compiled-source and
ELF checks confirm the benchmark is absent. The unfinished CLZ work is not
part of this production change.

The linked AAC audit verifies the 32,744-byte compact owner, native patch
provenance and late-SBR calls. The HTTP audit verifies the expected reader and
TLS EOF wrapper calls. The quiet-build audit verifies mode, clocks, disabled
diagnostics and the absence of boot benchmark sources.

## Installation and verification

Changing DIO to QIO requires installing the matching second-stage bootloader.
Application OTA alone preserves the old bootloader and its bus mode. ESP-IDF's
DIO ROM image header is intentional for QIO builds; runtime QIO is enabled by
the second-stage bootloader.

The installer privately backs up all 4 MiB, validates the partition layout and
writes only the bootloader and currently active application. Readback checks
the exact saved images and that changes are restricted to their programmed
sectors. NVS, SPIFFS, the partition table and OTA data are compared separately.
Wi-Fi, playlist and exposed settings are compared in memory before and after.

The production image started on the first reset. Readback confirmed both saved
images and unchanged NVS, SPIFFS, partition table and OTA data. The in-memory
comparison immediately after installation confirmed unchanged Wi-Fi, playlist
and exposed settings.

Twelve completed HTTP/EOF cases passed: MP3, FLAC, Vorbis, Opus, AAC-LC 48 kHz
stereo and HE-AAC 48 kHz stereo, each with AUTO and explicit selection. The user
then requested that the remaining checks be skipped. The controller and its
test child were stopped; the two HEv2 cases were not completed and the OTA
roundtrip was not started. The partial report is preserved unchanged, with a
separate `checks-skipped.json` record. No full-matrix or OTA pass is claimed for
this production image.

The radio was rebooted into its saved station. The final WebUI identity matches
ELF `54ec71b493261f3c00f86a649625c83e8c772b00eb2af5a3aae594c25e937094`,
and playback returned as AAC PCM, 44.1 kHz, stereo. The settings comparison cited
above was performed after flashing and before the interrupted tests; no second
in-memory comparison is claimed after terminating their controller.

This quiet image has no serial CPU/heap telemetry or register-printing boot
probe; actual register/read validation belongs to the earlier laboratory
images. HTTPS, ten-minute heap profiling and acoustic continuity were not
qualified by this deployment. The
[retained evidence](../tests/results/esp32c3-production-qio80-20261008/README.md)
contains the build, installation, completed cases and explicit skipped scope.
