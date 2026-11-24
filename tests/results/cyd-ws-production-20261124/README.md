# CYD production refresh after the shared WebSocket scheduler

Six normal board applications were built with the production wrapper from clean
tracked source `b65437a1bc59c9d269ce7bece597efddc70cea58`. They contain the shared
ESP Timer/event-loop scheduler; the optional RTC workspace remains **off**.
These are real Wi-Fi board applications, separately named from the OpenETH tests.

| Profile | Image bytes | Minimum free OTA bytes | Clang units | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| [vendor-pdm](../../../firmware/development/esp32-cyd2usb-native-ws-scheduler-20261124-vendor-pdm/app.bin) | 1,581,984 | 187,488 | 53 | 100 | 0 |
| [vendor-continuous](../../../firmware/development/esp32-cyd2usb-native-ws-scheduler-20261124-vendor-continuous/app.bin) | 1,576,032 | 193,440 | 53 | 98 | 0 |
| [vendor-legacy](../../../firmware/development/esp32-cyd2usb-native-ws-scheduler-20261124-vendor-legacy/app.bin) | 1,581,568 | 187,904 | 54 | 99 | 0 |
| [custom-flac-pdm](../../../firmware/development/esp32-cyd2usb-native-ws-scheduler-20261124-custom-flac-pdm/app.bin) | 1,555,312 | 214,160 | 53 | 100 | 0 |
| [custom-flac-continuous](../../../firmware/development/esp32-cyd2usb-native-ws-scheduler-20261124-custom-flac-continuous/app.bin) | 1,549,184 | 220,288 | 53 | 98 | 0 |
| [custom-flac-legacy](../../../firmware/development/esp32-cyd2usb-native-ws-scheduler-20261124-custom-flac-legacy/app.bin) | 1,554,640 | 214,832 | 54 | 99 | 0 |

Every image passes ESP32 identification, exact extent, segment checksum, appended
SHA-256, linked Xtensa ELF identity and both 0x1b0000-byte OTA slots. Compact
`app-metadata.json` accompanies each application. The [matrix](matrix.json) pins
local build artifacts and configuration; [frozen identities](qualification/artifact-snapshots.json)
were rechecked after the caches were reused for the RTC matrix. These are selected
artifact and translation-unit bindings, not a full compiler dependency closure.

Compared with the November 23 production settings, the only effective new key is
`YORADIO_WS_STATUS_RTC_SLOW=false`. Hardware/audio settings, two CPUs, five-second
task watchdog and 300 ms interrupt watchdog are preserved. TCP RX/mailbox/TX stays
11520/10/5760 and fixed TLS RX/TX stays 16384/4096. OpenETH, static TLS RX reserve,
early MPI, input reclaim, sampler and optional mono decoding remain disabled;
input remains limited to two channels. Vendor archives are unchanged.

Audio bindings remain stream core0/priority3/6144 bytes, decode
core1/priority5/16384 bytes, output core1/priority6/4096 bytes. Static decoder frames
are 1760 bytes with vendor FLAC and 1744 with custom FLAC; the Ogg word-page helper
is 2144 bytes. These do not measure total runtime stack depth.

Full Clang-Tidy completes **320 project units and 20 SDK frontend checks**, with
zero errors and exactly the same 594 reviewed warning occurrences. The
[warning catalog](clang-warnings.json) and per-profile comparisons retain existing
warnings; this is not a warning-free claim. The prior
[warning review](../cyd-aac-fairness-production-20261123/WARNING_REVIEW.md) still applies.

Final ELF checks place all 6560 WebSocket workspace bytes in ordinary DRAM and
the timer callback in Flash. [Opt-in RTC applications](../cyd-ws-rtc-production-20261124/README.md)
are a separate matrix. The [full TLS/HE-AAC/WebUI observations](../cyd-ws-shared-scheduler-20261124/README.md)
use diagnostic RTC-on applications; their finite passes do not qualify this
RTC-off profile for the same two-client HE-AAC memory workload. The retained
continuous-DAC timeout remains a separate runtime investigation.

Three pre-existing untracked tests were excluded from staging and production
compilation. Local logs/configuration extras are not published by this package.
The [C3 checkpoint](../cyd-production-refresh-20261117/README.md) remains separate;
no C3 implementation changed in this CYD refresh. Physical Wi-Fi/audio/RTC timing
and explicitly deferred custom Vorbis/private AAC scopes remain open.
