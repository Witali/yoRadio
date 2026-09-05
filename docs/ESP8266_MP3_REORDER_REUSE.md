# ESP8266 MP3 reorder / IMDCT workspace reuse

## Implementation

The native Helix decoder now borrows the first **198 int32 words (792 bytes)**
of channel 0's **576-word IMDCT output** while dequantizing/reordering short
blocks. `MP3ReorderBuffer()` returns the existing aligned integer storage;
it does not create a second owning pointer or cast it to a `DequantInfo_t`.

This is safe only with the current sequential granule pipeline:

1. Previous granule finishes synthesis and its synchronous PCM callback.
2. All current channels finish Huffman, dequantization and short-block reorder.
3. IMDCT writes its output, replacing the now-dead reorder scratch.
4. Synthesis consumes IMDCT output; the next granule may then reuse it.

Both the mono M/S fast path and stereo/fallback path use the same accessor.
Overlap history (`overBuf`), filter history and compressed bit reservoir are
not reused. DMA owns separate PDM buffers, not the IMDCT workspace.
Do not overlap dequantization with IMDCT/synthesis in future worker tasks
without disabling or redesigning this reuse.

Only IMDCT allocates and frees the storage. Reset clears the full IMDCT
output as before. Allocation-failure cleanup never frees scratch as a
second object. There are no new per-granule allocations, copies or locks.

## Configuration and memory

Enabled by default in the ESP8266 native component, independently of Mono or
Stereo. For a separate-buffer A/B build, configure CMake with
`-DYORADIO_ESP8266_MP3_SHARED_REORDER=OFF`; restore `ON` for the optimized build.
This maps to `YORADIO_HELIX_MP3_SHARED_REORDER=0/1` in shared Helix sources.
Other targets default to their previous separate allocation.

The change removes **792 bytes of requested DRAM heap allocation** and one
allocation/free pair per decoder lifetime. Allocator overhead is additional
and has not been measured on the board. It does not enlarge the 16-KiB IRAM
reservation, shrink stacks, or change input/PCM/DMA buffer sizes. It is an
additional saving on top of the previous mono PCM reduction of 1152 bytes.

The host checked-allocator results (64-bit host structures, not device RAM):

| Layout | Byte-addressed objects | Word objects | Allocations |
| --- | ---: | ---: | ---: |
| Separate reorder | 7612 B | 15636 B | 13 |
| Shared reorder | 6820 B | 15636 B | 12 |

Xtensa GCC 8.4/O3 build: static DRAM remains 20840 bytes, IRAM
vectors/text/bss remains 27384 bytes, `_iram_end=0x40106af8`. Flash text is
96 bytes smaller than the preceding mono build. `m_DequantInfo` is absent
from the optimized ELF. Disassembly of MP3 `DequantBlock` and `DequantChannel`
contains word stores and no 8/16-bit stores, preserving IRAM access rules.

## Verification, 2026-09-05

- **331 host tests pass** (55.25 seconds).
- Separate/shared builds produce **identical PCM bytes**, not merely a
  similar SNR: six MP3 vectors, Mono and Stereo, full-frame and granule APIs.
- Includes MPEG1/2/2.5, original mono, 320-kbit/s noise and stereo-mode changes.
- Direct reorder checks cover short/mixed blocks at all nine sample-rate
  table entries, both channels, scratch-boundary canaries and unchanged
  overlap histories.
- Allocation failure injected at every MP3 allocation; cleanup, repeated
  free, reset and 50 AAC/MP3 allocation cycles pass without live allocations.
- Ordinary Mono firmware builds with Xtensa GCC O3 and profiling disabled.

Run `node --test --test-name-pattern="shared MP3 reorder" tests/esp8266-helix-golden.test.js`
for the focused A/B tests. Full output is saved in
`docs/benchmarks/esp8266-reorder-2026-09-05/regression.log`.

The application and manifest are under
`firmware/development/esp8266-native-mono-reorder/`.

## Physical installation and smoke test, 2026-09-05

The archived 686848-byte image was flashed to app0 at `0x10000` on the Wemos
D1 mini, with esptool hash verification and a local backup of the preceding
application. Bootloader, partition table, NVS, SPIFFS and OTA selection were
not written. Boot confirmed CPU 160 MHz, GPIO3 I2S-PDM32, two 512-word DMA
buffers, restored station 498 / volume 254, and a 511-station playlist index.
The board obtained `192.168.100.6`; `/` returned HTTP 200.

A short WebSocket toggle/stop test received 11 frames and confirmed ROCK FM
MP3 128 kbit/s playback, then restored the original stopped state. The first
stream-open attempt failed with -4; the next attempt returned HTTP 200.
The stream was still connecting at the 7-second observation and playing at
17 seconds. No OOM, panic or reset appeared in the captured application log.

The physical decoder reported **9528 bytes DRAM and 16384 bytes IRAM**,
versus the previously measured stereo/separate-reorder DRAM value 11472:
1944 bytes less, matching 1152 bytes of mono PCM plus 792 bytes of reorder
scratch. This comparison is decoder workspace, not a matched RF-load heap
benchmark. One playing snapshot reported free heap 12532 bytes, minimum heap
10572 bytes and web stack headroom 2336 bytes; after stopping, free heap was
24024 bytes. The three post-command status requests took 34-36 ms; this
short sample is not a comprehensive WebUI responsiveness test.

Raw results: `docs/benchmarks/esp8266-reorder-2026-09-05/hardware-smoke.log`
and `hardware-playback.log`. Long-run stability, AAC playback, CPU timing
and listening remain untested for this image. Previous firmware artifacts
remain available. PCM output still uses 576 samples/channel per callback;
the discussed 64/128-sample chunking has not been implemented.
