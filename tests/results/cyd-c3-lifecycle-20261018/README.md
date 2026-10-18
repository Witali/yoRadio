# CYD audio lifecycle transfer

The software stage passes host regressions and all three native ESP32 builds.
Runtime source commit: `2df73834`. ESP-IDF: pinned v6.0.2, GCC toolchain
`esp-15.2.0_20251204`. Physical playback/DMA/analog acceptance remains pending.

## Saved application images

| Variant | Bytes | Application and metadata |
| --- | ---: | --- |
| Original PDM, source `42bc7bd4` | 1350720 | [Baseline](../../../firmware/development/esp32-cyd2usb-native-pdm-baseline/manifest.json) |
| PDM after lifecycle transfer | 1352352 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-pdm/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-pdm/manifest.json) |
| Continuous DAC | 1346320 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-dac/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-dac/manifest.json) |
| Legacy DAC | 1352400 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-legacy-dac/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-legacy-dac/manifest.json) |

Every image fits the existing 0x1b0000 OTA slot. Exported image hashes match
their build outputs; embedded ELF hashes match the corresponding ELF files.
The three final application descriptors identify source commit `2df73834`
without a dirty suffix. Original and final PDM normalized sdkconfig values
match exactly; the application-size increase is 1,632 bytes.

An intermediate PDM rebuild failed because a local reconstruction of sdkconfig
serialized a hexadecimal field incorrectly (`0x32768` instead of `0x8000`).
No image was exported from that attempt. Restoring the normal checked-in
defaults and rebuilding passes; final configuration equivalence is checked
against the saved baseline. This was a build-preparation error, not a firmware
runtime failure.

## Executable host coverage

[The report](report.json) records source hashes and compiler version.
[The runner](../../run-cyd-lifecycle.py) compiles actual pipeline tasks,
state functions and PDM flush/reset functions under ASan/UBSan. Codec and
hardware APIs are mocks; host mutexes provide actual mutual exclusion.

- Delayed PCM and multiple cached EOS frames precede terminal publication.
- Decoder and independent PCM workspace are freed on EOF, Stop, allocation
  failure and decode failure. Empty terminal packets do not open a decoder.
- Old encoded/PCM packets and stale state callbacks cannot affect a new Play.
- Play while output wakes discards the old software tail, including equal-rate
  transitions. Two host threads issue 2,000 Play/Stop operations per variant.
- Queue waits can be cancelled by a generation change; failures do not spin
  forever waiting for old PCM or overwrite a newer command.
- PCM packet boundaries preserve complete sample frames and word alignment.
- PDM flush pads and sends a partial block once; discard resets history and
  cannot replay a previous tail.
- Espressif, Helix and minimp3 service branches all pass. This tests their
  service ownership with codec mocks, not the decoder arithmetic themselves.

The existing C3 EOF harness passes with the common completion header.
Source/WebUI/settings regressions pass 57/57. Initial and reviewed full lint
results for C3 and CYD remain in [the analysis campaign](../native-lint-20261018/).
