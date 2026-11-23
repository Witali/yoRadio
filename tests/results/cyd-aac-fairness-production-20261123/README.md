# CYD production refresh after AAC memory and decoder fairness changes

All six normal GCC board profiles were built and exported from clean tracked
source `823534ed2b446eac128082d2adedfb15d1274412`, using the pinned ESP-IDF
6.0.2 production wrapper. They include the 8 KiB initial public AAC PCM buffer,
AAC's release of excess idle input slots, and the elapsed-time decoder fairness
fix. The vendor codec archives are unchanged. The previous November 17 images
are retained in their separate development directories.

| Profile | Image bytes | Minimum free OTA bytes | Clang units | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| [vendor-pdm](../../../firmware/development/esp32-cyd2usb-native-aac-fairness-20261123-vendor-pdm/app.bin) | 1,581,712 | 187,760 | 53 | 100 | 0 |
| [vendor-continuous](../../../firmware/development/esp32-cyd2usb-native-aac-fairness-20261123-vendor-continuous/app.bin) | 1,575,728 | 193,744 | 53 | 98 | 0 |
| [vendor-legacy](../../../firmware/development/esp32-cyd2usb-native-aac-fairness-20261123-vendor-legacy/app.bin) | 1,581,296 | 188,176 | 54 | 99 | 0 |
| [custom-flac-pdm](../../../firmware/development/esp32-cyd2usb-native-aac-fairness-20261123-custom-flac-pdm/app.bin) | 1,555,040 | 214,432 | 53 | 100 | 0 |
| [custom-flac-continuous](../../../firmware/development/esp32-cyd2usb-native-aac-fairness-20261123-custom-flac-continuous/app.bin) | 1,548,912 | 220,560 | 53 | 98 | 0 |
| [custom-flac-legacy](../../../firmware/development/esp32-cyd2usb-native-aac-fairness-20261123-custom-flac-legacy/app.bin) | 1,554,368 | 215,104 | 54 | 99 | 0 |

Each saved application passed ESP32 chip identification, segment checksum,
appended SHA-256, exact image extent, linked Xtensa ELF identity and both
`0x1b0000`-byte OTA slot checks. Compact `app-metadata.json` accompanies each
image. The exporter used `--allow-dirty` for exactly three pre-existing
untracked tests; all tracked source was clean and no test units were compiled
into these applications. Raw build products/logs remain local and are pinned
in the [matrix](matrix.json).

All six text and JSON SDK configurations are byte-for-byte unchanged from
their previous production configurations. The normal TCP RX window/mailbox
remains 11,520/10 and TX remains 5,760 bytes. Full 16,384/4,096-byte fixed TLS
buffers remain selected. OpenETH, test certificates, the sampler, raw Opus,
static TLS RX loan, early MPI and input reclaim remain disabled. The default
source-channel limit is two; optional Helix mono decoding is not selected.

Task bindings remain stream on core 0, priority 3, stack 6,144 bytes; decode
on core 1, priority 5, stack 16,384; output on core 1, priority 6, stack 4,096.
All six ELF frame checks pass: decoder is 1,760 bytes with vendor FLAC and
1,744 with custom FLAC; the Ogg word-page helper is 2,144 bytes. These static
frames do not measure total runtime stack depth.

Clang-Tidy covers 320 project units and 20 SDK frontend checks with no errors.
For each profile, warning file/check/message/multiplicity exactly matches the
previous reviewed catalog. The compiler/libc configuration differences also
match the previous matrix. [Warning review](WARNING_REVIEW.md) and
[exact sites](clang-warnings.json) retain the distinction between no new
warnings and warning-free code.

A read-only ELF section review confirms that selected large codec tables and
the certificate bundle already reside in `.flash.rodata`. They cannot simply
be moved out of RAM to recover heap. The 5,168-byte display context and
5,120-byte WebSocket status buffer remain in DRAM. Display DMA and the existing
maximum escaped-JSON test require separate analysis before reducing these
buffers; this refresh does not change them.

The [full-application HE-AAC QEMU comparison](../cyd-aac-resource-profile-20261123/README.md)
qualifies separate diagnostic OpenETH applications with optional TCP profiles.
These normal board images retain the original network defaults: the complete
HE-AAC/WebUI resource control on that default profile remains NONPASS.
No physical Wi-Fi, audio timing, listening test or universal codec conformance
is claimed. The previous [C3 image and host regression](../cyd-production-refresh-20261117/README.md)
remain the C3 checkpoint; C3 was not rebuilt by this six-profile refresh.
