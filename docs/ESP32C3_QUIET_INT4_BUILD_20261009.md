# ESP32-C3 quiet integer-clock candidate, 2026-10-09

## Status

A production-profile candidate is built and saved, with linked-code audits
passing. **This exact image has not yet been installed or qualified on the
board.** The concurrent cross-codec/TLS campaign uses the older diagnostic
integer4 image. Its results must not be presented as hardware acceptance of
this quieter build.

[Firmware manifest](../firmware/development/esp32c3-idf-6.1-r9a97-quiet-int4/manifest.json)
and [application](../firmware/development/esp32c3-idf-6.1-r9a97-quiet-int4/app.bin):

- Version: `idf61-quiet-int4`; ESP-IDF revision `9a97f6c54ec6`.
- App size: **1,454,784 B**.
- App SHA-256: `9dcee95546181c331c9c3c0a6c3693985f269fff90abb195151af174305237b0`.
- ELF SHA-256: `11e8ee4514cdffd9400e57f8e4954da8131c2e392fa35157aa3378484e166746`.

## Selected configuration

The build uses QIO 80 MHz, the ordinary integer PDM divider and full compact
AAC/SBR/PS at native rates. The RX-only TLS reserve is 17,058 B; adaptive input
starts at its minimum, with 250/500 ms minimum/maximum prefill. Four additional
input slots can be allocated after the first custom-FLAC frame, subject to
the existing heap guard, and retire on Stop/EOF/codec changes.

This is a candidate selection, not a change to repository defaults. Expanded
input reduced delayed-DMA events in the [pause comparison](ESP32C3_DELIVERY_PAUSES_20261009.md)
but did not eliminate them. Final memory, uninterrupted playback and OTA
qualification are still required.

Console, logging, profiling, deep sleep, heap-owner/TCP probes and direct-DMA
PCM are disabled. The trust bundle is byte-identical to the previous quiet
production image's normal roots; no laboratory CA is included. The config
audit rejects populated Wi-Fi/password/secret settings. No board NVS or user
credentials are copied into these firmware artifacts.

## Build checks

| Linked region | Bytes |
| --- | ---: |
| IRAM text | 46,184 |
| Initialized DRAM | 11,524 |
| DRAM BSS | 44,848 |
| Flash text | 1,085,418 |
| Flash rodata | 308,308 |

Configuration comparison against `quiet-min250` permits exactly the switch
back to the ordinary divider and selection of four extra FLAC slots. Current
source includes the input-retention repair. Allocator, HTTP and full-AAC link
checks pass, including the reserved RX buffer and normal EOF PCM flush/discard
paths. Compile-command and symbol checks exclude CLZ, flash probing, profiling
and the alternative direct-DMA output implementation.

All **119 nonempty text/rodata sections in 18 AAC/FLAC objects** match the
previous quiet build byte for byte. This supports unchanged codec arithmetic
and precision; it is not a new PCM or analog measurement. Pipeline scheduling,
allocation and network behavior still need testing on this exact image.

[Frozen build evidence](../tests/results/esp32c3-quiet-int4-build-20261009/README.md)
contains scripts, checks, source overlays and byte hashes. Both the saved
application and bootloader are retained; the current board is not modified
by this build.
