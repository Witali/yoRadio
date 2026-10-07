# ESP32-C3 main integration — 7 October 2026

## Selection

Merge `7991b312` (the station-timeout checkpoint) into the previous main,
`ddda1f66`. The merge commit is `a4ef7d77`. This keeps the original development
history, tests and experimental options, without enabling unqualified modes
in the default production configuration.

The five later commits on `codex/aac-storage18`, from `91bc298d` through
`6c21c8a9`, are excluded. They contain the latest RX-copy telemetry, packet
ownership measurements and startup packet-pool design. A startup RX pool is
not implemented or enabled by this merge. Earlier experimental sources and
their evidence remain in the merged history.

## Included behavior

| Area | Integrated change | Default status |
| --- | --- | --- |
| AAC | Actual profile/channel/rate metadata, full-rate SBR output, 8 KiB PCM workspace and adaptive ADTS allocation | Enabled; no new 22 kHz cap |
| Wi-Fi memory | Selected Wi-Fi routines placed in flash instead of IRAM | Enabled |
| CPU measurements | Profiling without a separate profiling task and stack | Included |
| Vorbis | Allocation failure handling, lifecycle/registration cleanup, output retries and final PCM/EOF handling | Repair enabled |
| FLAC | Bounds/depth fixes and exact predictor optimizations | Custom decoder enabled |
| Decoder teardown | Correct terminal ownership and resource cleanup | Enabled |
| Station availability | Bounded retries and persisted WebUI timeout, 1–120 seconds, default 10 | Enabled |
| AAC compact structures / early reservation | Research implementations and precision/allocation evidence | Opt-in |
| Direct DMA PCM and output-task priority 8 | Implementations and comparison evidence | Opt-in |
| RX diagnostics, native L2-to-L3 copy and TCP PCB pool | Existing experiment switches | Off |

This is not a claim that all HE-AAC streams fit the default C3 memory budget.
Historical heap/continuity failures remain recorded. In particular, raising
output priority improved scheduling but did not establish uninterrupted
playback for every demanding FLAC stream. CPU utilization is informational;
remaining memory and continuity failures are the reasons for retaining opt-in
status. See [the priority comparison](ESP32C3_OUTPUT_PRIORITY_20261006.md),
[Vorbis output checks](ESP32C3_VORBIS_OUTPUT_20261005.md) and
[station timeout behavior](ESP32C3_STATION_TIMEOUT.md).

## Integration fixes

- `544ff03b`: default builds now reserve two FreeRTOS task-local pointers.
  Pthread owns slot 0; AAC uses slot 1. The static assertion correctly caught
  the missing default during the first clean build.
- `785dd3a8`: refresh host stubs and the PCM call signature; ignore comments
  and string literals in the integer-only source guard; check the configurable
  timeout instead of the removed fixed constant.

## Verification

| Check rerun on the integration tree | Result |
| --- | --- |
| Clean-default ESP-IDF 6.0.2 production build | PASS after the TLS default fix |
| Selected Node regressions: C3, shared audio/WebUI and Helix golden cases | 243/243 PASS, no skips |
| 21 Python test scripts, including retained evidence and RV32 ABI checks | 133/133 PASS, no skips |
| Host stream-format/AAC allocation suite with ASan and UBSan | PASS |
| Host delayed-PCM/EOF/stop/error suite | PASS |
| Custom decoder terminal ownership | 17 cases PASS |
| Actual configuration and linked AAC/Vorbis repair symbols | PASS |

The exact Node selection and Python script list, logs, checksums and initial
issues are retained in
[`tests/results/esp32c3-main-integration-20261007`](../tests/results/esp32c3-main-integration-20261007).
Evidence replay tests verify recorded outcomes, including expected failures;
they are not new physical-board or QEMU runs. The unrelated full ESP8266 Opus
research matrix was not rerun to completion.

## Saved firmware

[`firmware/development/esp32c3-main-merge-20261007`](../firmware/development/esp32c3-main-merge-20261007)
contains the application, exact SDK configuration and provenance manifest.
The application is 1,401,008 bytes in a 1,900,544-byte OTA slot (26% spare).
It uses DIO 80 MHz, full AAC Plus, the Vorbis repair, and no deep sleep.
Experimental compact AAC, direct DMA, priority override and RX modes are off.

The image was built before committing the TLS fix, so its embedded version
contains `a4ef7d77-dirty`; the manifest identifies the committed firmware
source and the exact binary/configuration hashes. This is an unreleased
build-only artifact. It was not flashed or tested on the physical board in
this integration task; the board's installed image was not changed.
