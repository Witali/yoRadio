# Experimental CYD production images with RTC SLOW workspace

Six normal Wi-Fi production applications were built from clean tracked source
`b65437a1bc59c9d269ce7bece597efddc70cea58` with the WebSocket shared scheduler
and the optional RTC workspace enabled. Each differs from its matching
[normal production profile](../cyd-ws-production-20261124/README.md) only by
`YORADIO_WS_STATUS_RTC_SLOW=false` becoming `true`. The option remains
experimental and disabled by default. No physical board was connected.

| Profile | Image bytes | Minimum free OTA bytes | Focused Clang units | Existing warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| [vendor-pdm](../../../firmware/development/esp32-cyd2usb-native-ws-rtc-20261124-vendor-pdm/app.bin) | 1,588,544 | 180,928 | 1 | 1 | 0 |
| [vendor-continuous](../../../firmware/development/esp32-cyd2usb-native-ws-rtc-20261124-vendor-continuous/app.bin) | 1,582,592 | 186,880 | 1 | 1 | 0 |
| [vendor-legacy](../../../firmware/development/esp32-cyd2usb-native-ws-rtc-20261124-vendor-legacy/app.bin) | 1,588,128 | 181,344 | 1 | 1 | 0 |
| [custom-flac-pdm](../../../firmware/development/esp32-cyd2usb-native-ws-rtc-20261124-custom-flac-pdm/app.bin) | 1,561,872 | 207,600 | 1 | 1 | 0 |
| [custom-flac-continuous](../../../firmware/development/esp32-cyd2usb-native-ws-rtc-20261124-custom-flac-continuous/app.bin) | 1,555,744 | 213,728 | 1 | 1 | 0 |
| [custom-flac-legacy](../../../firmware/development/esp32-cyd2usb-native-ws-rtc-20261124-custom-flac-legacy/app.bin) | 1,561,200 | 208,272 | 1 | 1 | 0 |

Every saved application passes ESP32 chip identification, segment checksum,
appended SHA-256, exact image extent, linked Xtensa ELF/application descriptor
identity and both `0x1b0000`-byte OTA slot checks. The production wrapper
saved each image and compact `app-metadata.json` under a fresh development
variant; older images and versioned releases were retained. The exporter
allowed exactly three pre-existing untracked tests while tracked source
remained clean; none of those test units entered the applications.

## Storage and unchanged production policy

All six linked ELFs move the same five workspace objects, totaling 6,560
bytes, to `.rtc.force_slow` within `0x50000000..0x50002000`. Ordinary DRAM
BSS and `_heap_start` each decrease by exactly 6,560 bytes relative to the
matching normal ELF. This is a static placement gain, not a measured runtime
heap minimum. JSON remains 5,120 bytes, with two clients and unchanged
snapshots and socket-list capacities.

Normal-network RTC usage is **6,600 bytes**, with **1,568 bytes free** below
the separate **24-byte SDK reservation**: 6,600 + 1,568 + 24 = 8,192.
The [diagnostic runtime archive](../cyd-ws-shared-scheduler-20261124/README.md)
uses **6,664 bytes** and has **1,504 bytes free** because its separate
64-byte RTC access probe is included. These are different configurations.
The timer callback remains in `.flash.text`; atomics, producer/playlist
control, timer handle and 5,168-byte DMA-backed display context remain in
ordinary DRAM. ULP is disabled. No audio, codec or DMA buffer moves to RTC.

Normal Wi-Fi, TCP RX 11,520 / mailbox 10 / TX 5,760, full fixed TLS
16,384/4,096, the five-second task watchdog and 300 ms interrupt watchdog
remain unchanged. OpenETH, diagnostics, custom test certificates, dynamic
TLS, the separate static-RX loan, early MPI, input reclaim and raw Opus are
off. Input remains limited to two channels; optional mono decoding is off.
Vendor/custom FLAC choices and PDM/continuous/legacy hardware options are
preserved for each profile.

| Audio task | Core | Priority | Stack bytes |
| --- | ---: | ---: | ---: |
| Stream | 0 | 3 | 6,144 |
| Decoder | 1 | 5 | 16,384 |
| Output | 1 | 6 | 4,096 |

Static compiler frame checks remain 1,760 bytes for the vendor-FLAC decoder,
1,744 for custom FLAC and 2,144 for the Ogg word-page helper. They do not
measure total runtime stack depth.

## Focused Clang and evidence

The RTC follow-up analyzes the actual complete `websocket_service.c`
translation unit and included headers once per profile: **six units**, zero
errors. Every profile retains the same one reviewed
`bugprone-narrowing-conversions` warning at the `int` to `int8_t` assignment.
File/check/message/severity/multiplicity exactly matches the corresponding
normal result. The thirteen typed compiler/libc configuration differences
also match the reviewed normal matrix, including absent versus false values.
The separate [normal campaign](../cyd-ws-production-20261124/README.md)
contains the full 320-project-unit and 20-SDK-frontend qualification; those
counts are not attributed to this focused RTC follow-up.

[Matrix](matrix.json), [warning sites](focused-clang-warnings.json),
[selected artifact identities](artifact-identities.json) and
[input bindings](inputs.json) link every profile to its image, frozen
GCC/Clang configuration/compile database and selected source/tool bytes.
Each `qualification/<profile>/` directory preserves image/OTA checks,
typed configuration deltas, linked workspace/DRAM/heap symbols, frames and
focused Clang results. These are selected evidence and command bindings,
not a complete compiler dependency closure or a self-contained build cache.
Full ELF/map, compiler databases, build logs and raw configurations stay local.

The first focused controller stopped while reading a temporarily empty
concurrent status write, before the next compiler check. Its original
NONPASS is retained; the continuation validates/reuses the first successful
profile and completes the other five. An aggregation helper also first
treated an absent disabled mono symbol as an error; the corrected check
uses the unchanged typed configurations. The
[controller history](qualification/controller-history.json) preserves these
helper outcomes separately from production/compiler and runtime results.

The [local candidate precheck](local-precheck.json) covers these six images
and metadata only. Its generic matches were the exact NUL-terminated public
SDK parser delimiter constants, with no PEM bodies or unreviewed findings.
It does not replace the final Git/LFS payload, history and ref inspection.

## Reproduction and open acceptance

Use the pinned source, SDK/vendor revisions and tools in `inputs.json`.
Start with the matching qualified normal configuration and change only
`CONFIG_YORADIO_WS_STATUS_RTC_SLOW` from disabled to `y`. Keep the selected
backend and codec defaults; do not substitute C3 hardware configuration.
The [production wrapper](../../../idf/esp32-cyd2usb-native/build-production.ps1)
requires the configuration inside its selected build directory. Use a fresh
variant and save every successful handoff in `firmware/development`:

```powershell
.\idf\esp32-cyd2usb-native\build-production.ps1 -DependencyRoot $dependencies -AudioBackend pdm -BuildDirectory $build -Sdkconfig $configPath -Variant $freshVariant
```

For focused Clang, reconfigure the matching Clang profile with RTC enabled,
retain the typed compiler/libc delta, then run the pinned `clang-tidy` with
the generated compile database and repository `.clang-tidy` on the whole
WebSocket translation unit. The normalized commands and original database
identities in `inputs.json` record the actual input bindings.

These production exports do not rerun or reclassify the
[shared-scheduler runtime outcomes](../cyd-ws-shared-scheduler-20261124/README.md).
The first continuous-DAC full TLS/HE-AAC run remains a genuine output-timeout
**NONPASS**, even though its exact-image control passed. Earlier allocation
and client failures in the [RTC runtime archive](../cyd-ws-rtc-memory-20261124/README.md)
also retain their original outcomes. Repeatability, useful memory margin,
physical Wi-Fi/audio, RTC latency and sleep/wake acceptance remain open.
No universal codec conformance or physical listening test is claimed.
