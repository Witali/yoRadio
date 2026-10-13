# ESP32-C3 RAM categories — 2026-10-13

## Scope and accounting

Source: `codex/esp32c3-idf-upgrade`, production-derived `web-upload2k` config,
ESP-IDF `9a97f6c54ec638111ce55cd36581b3c192f15207`. Shared decoder arena and
direct DMA PCM are disabled. The last verified board restoration in this
thread was `idf61-production-prefill1000`; this is not a fresh board reading.
The new stream-probe build does not change these buffer policies.
1 KiB = 1,024 bytes.

These are allocation categories, not mutually exclusive linker sections.
For example, the static TLS reserve and output staging buffer already belong
to `.dram0.bss`; do not add them again to a linker-section total. Task stacks
and most SDK buffers are allocated from the system heap. Code in IRAM also
uses internal SRAM. Free bytes and the largest contiguous block are different
quantities. Unused bytes inside a private decoder arena cannot fund TLS/Wi-Fi.

## Common allocations

| Category | Capacity / policy | Lifetime and exclusions |
|---|---|---|
| Wi-Fi static RX | 6 buffers, approximately 1.6 kB each (about 9.4 KiB total) | SDK allocation at Wi-Fi initialization; this is not the total Wi-Fi footprint |
| Wi-Fi dynamic packets | Up to 16 RX and 16 TX buffers | Variable frame-sized allocations; limits are not permanent reservations |
| TCP/IP and HTTP | Dynamic pbufs, sockets, TCP state, HTTP headers | TCP receive window is 8,640 bytes per configured default, not a separately preallocated 8,640-byte application buffer |
| TLS receive reserve | **17,058 bytes / 16.66 KiB** | Static, present even for HTTP; one reserved RX allocation, including record overhead |
| Other TLS memory | Dynamic | TX maximum record payload 4,096 bytes, plus overhead; handshake, certificates, crypto and connection state are additional. The RX reserve does not cover all TLS allocations |
| Compressed input queue | Floor: 4 slots × 2,060 bytes = **8,240 bytes** (8,192 payload) | Configuration minimum is 5 × 1,600 = 8,000 bytes, rounded up to four actual packets. Queue control/semaphores and allocator overhead are extra |
| FLAC input expansion | Up to 4 additional slots: another **8,240 bytes** | Subject to configured queue target and 32 KiB system-heap headroom; eight resident slots are not guaranteed |
| HTTP audio read scratch | **2,048 bytes** | Stream-task allocation, separate from compressed packets |
| PCM output queue | **8,192 bytes** | Ring storage includes queued item overhead; decoder workspace is separate |
| Output staging | **2,048 bytes** | Static stereo int16 buffer: 512 frames × 2 channels × 2 bytes |
| I2S/PDM DMA payload | **8,192 bytes** | Four descriptors × 512 stereo int16 frames; descriptors, driver objects and completion queue are extra |
| Audio task stacks | **24,576 bytes / 24 KiB** | Stream 6 KiB + decoder 16 KiB + output 2 KiB; task control blocks are extra |
| WebUI task stacks | **16 KiB** for HTTP + static workers | HTTP 8 KiB + two static-worker stacks of 4 KiB. Each worker's 2 KiB download buffer is inside its stack, not extra |
| WebSocket status stack | **4 KiB** | Also performs delayed reboot; no newly allocated reboot task |
| SPIFFS upload staging | **2 KiB temporarily** | New WebUI implementation: allocated only for file upload, freed after receive; filesystem metadata/cache remain separate |
| OTA staging | **4 KiB temporarily**, plus context | Direct OTA partition API; not SPIFFS and not covered by the file-upload buffer |
| Other services | Additional stacks and state | Display, buttons, time, Wi-Fi/SDK tasks, NVS, SPIFFS, HTTP/WebSocket clients and application globals; not fully attributed here |

The stream-probe state is allocation-free and lives on the existing stream
task stack. Its host ABI size is 40 bytes; target stack usage must be read
from the build evidence rather than inferred from the host layout.

## Codec workspace by format

The following are **maximum sampled live requested bytes** in the isolated
100 KiB decoder-arena experiment. They include decoder allocations, the
decoder's PCM workspace and parsing buffers routed into that arena. They
exclude allocator metadata, alignment and temporary old/new realloc overlap.
They are evidence for these fixtures, not maximum requirements for all files.
Do not add the PCM workspace a second time to the codec column.

| Format tested | Codec + local workspace | Notes |
|---|---:|---|
| MP3 320 kbit/s | **41,340 B / 40.37 KiB** | Espressif decoder; generic PCM workspace starts at 12 KiB and can retain/grow capacity |
| FLAC level 8 | **53,024 B / 51.78 KiB** | Custom FLAC; input queue and DMA remain outside |
| AAC-LC 320 kbit/s | **60,620 B / 59.20 KiB** | Includes 8 KiB AAC PCM workspace |
| HE-AAC 48 kHz stereo | **94,032 B / 91.83 KiB** | Includes compact SBR storage and 8 KiB PCM workspace |
| HE-AACv2 44.1 kHz stereo | **93,776 B / 91.58 KiB** | Includes PS and SBR |
| AAC parameter transitions | **94,288 B / 92.08 KiB** | Largest sampled requested live value across the cited transition fixtures |

**Normal profile:** allocations come from the shared system heap and are
released/reused according to their lifetime; no permanent 100 KiB codec block.
**Experimental arena:** a static 102,400-byte private heap is reserved for any
codec. MP3 still occupies the whole reservation from the system's perspective;
58,148 bytes observed free inside it are unavailable to Wi-Fi/TLS. HE-AAC had
only 4,660 sampled free arena bytes. The 96 KiB arena failed an AAC transition;
100 KiB handled the tested allocation cases but is not production-qualified.

## Observed system-heap headroom

| Scenario | No arena: free / largest | 100 KiB arena: free / largest |
|---|---:|---:|
| MP3 HTTP | 83,724 / 65,536 B | 22,992 / 10,240 B |
| HE-AAC 48 kHz HTTP | 38,036 / 28,672 B | 30,956 / 10,240 B |
| HE-AAC HTTPS, 60 s | 25,036 / 10,240 B | 18,372 / 4,608 B |

These are minima sampled in the October 12 campaign, not simultaneous paired
samples or guaranteed floors. Separate October 13 WebUI/FLAC control snapshots
showed 64,436 then 64,312 bytes free, largest block 47,104 bytes, during the
short active FLAC/download window. Conditions differ; this is not an exact
codec-only RAM comparison with the table above.

The HTTP/HTTPS heap difference cannot be assigned entirely to TLS: TCP/Wi-Fi
packets, WebUI requests and measurement timing also vary. A complete additive
Wi-Fi/TLS/SDK breakdown requires owner-aware live allocation tracing. Do not
label the unclassified residual as either codec memory or Wi-Fi memory.

## Evidence

- [Shared arena measurements and failures](ESP32C3_SHARED_DECODER_ARENA_20261012.md)
- [FLAC input capacity and DMA investigation](ESP32C3_ARENA_FLAC_DMA_20261013.md)
- [WebUI allocation measurements](ESP32C3_WEB_MEMORY_20261013.md)
- [Exact WebUI candidate configuration](../firmware/development/esp32c3-idf-6.1-r9a97-web-upload2k/sdkconfig)
- [FLAC control snapshots](../tests/results/esp32c3-web-memory-20261013/physical-03/results.json)

Static Wi-Fi buffer sizing follows the pinned SDK's
`components/esp_wifi/Kconfig` help text. Other capacities are taken from
`audio_service.c`, `board_config.h`, `native_audio_output.c`, `decoder_pcm.h`,
`tls_large_reserve.c`, `tls_input_reserve.c` and `adaptive_input.c`.
