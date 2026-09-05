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
`firmware/development/esp8266-native-mono-reorder/`. **Not flashed**: on-board
heap/CPU timing, RF-load stability and listening checks remain unmeasured.
Previous development binaries and the physical board are unchanged.
