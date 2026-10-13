# ESP32-C3 runtime memory reservation plan

## Objective and baseline

Reduce allocation failures and fragmentation without removing audio formats,
changing decoded PCM, or introducing playback gaps. Work through the following
steps separately; measure each step against the same firmware configuration.

The shared-decoder-arena HE-AAC HTTPS trial left 18,372 bytes of system heap,
a largest free block of 4,608 bytes, and a separate 17,058-byte TLS RX reserve.
That completed trial had no allocation failures or DMA drops. A small largest
block alone is not a failure: check the actual remaining allocation sizes and
lifetimes. Other startup trials still had allocation failures. See
[arena measurements](ESP32C3_SHARED_DECODER_ARENA_20261012.md) and
[FLAC investigation](ESP32C3_ARENA_FLAC_DMA_20261013.md).

## Ordered implementation

1. **Bound WebUI memory and remove late reboot-task allocation.** Replace
   whole-body uploads (up to 96 KiB plus a terminator) with streaming multipart
   reception and temporary files. Keep credential validation and the existing
   browser form contract. Reject interrupted/malformed uploads without publishing
   their incomplete file. Schedule reboot through an existing task, including
   OTA, after queuing the response. Verify file bytes, concurrent downloads,
   upload errors, settings preservation, and OTA success/failure.
   - Downloads already stream through two independent 2 KiB stack buffers.
     These stacks are allocated before HTTP accepts requests: **4 KiB total is
     already reserved at startup**, with no per-download payload allocation.
     Keep that baseline; make the buffer size explicit/configurable. Test 4 KiB
     per worker (8 KiB total) only with memory/throughput evidence. Never share
     an unprotected buffer between simultaneous requests. Do not count moving
     stack storage to static RAM as a memory saving.
   - Final user preference: keep download chunks at 2 KiB per worker. For rare
     SPIFFS uploads allocate one **2 KiB staging buffer on demand**, reuse it
     across the request's files, and free it before publication. Do not reserve
     this payload buffer at boot. A failed allocation must leave live files
     unchanged. OTA retains its separate existing 4 KiB buffer and direct
     partition writes; it does not pass through SPIFFS.
   - Measure removed request-sized heap allocation, persistent RAM changes,
     stack high-water marks, and residual SDK/filesystem allocations separately.
2. **Guarantee the minimum audio input queue at startup.** Reserve a bounded
   pool, keep used packets alive, and free/reuse only unowned blocks. Compare
   heavy FLAC and HE-AAC HTTPS, starvation, DMA drops, and total/largest heap.
3. **Measure concurrent TLS/HTTP allocations before extending reserves.**
   Trace startup, handshake, certificate validation, reconnect, station changes,
   and WebUI activity. Account for the existing 17,058-byte RX reserve. Reuse
   connection/decoder storage only after every pointer owner has released it.
4. **Tune network pools last.** Compare Wi-Fi RX/TX and lwIP pool options with
   measured burst/concurrency demand; preserve a separate working margin for
   Wi-Fi, cryptography, and WebUI. Do not reserve all remaining heap blindly.

## Evidence and acceptance

- Record firmware/source hashes, exact sdkconfig, test conditions, and failures.
- Separate calculated byte savings from physical measurements. Free bytes inside
  a decoder-private arena cannot satisfy system/TLS allocations.
- Check total free heap, largest block, lifetime minimum, allocation failures,
  task stacks, input/output waits, DMA drops, and watchdog/reset events.
- Use repeatable fixtures, include simultaneous WebUI activity, and preserve
  the board's settings and original firmware. Keep private data in memory only.
- No blanket 8 KiB largest-block gate: use measured allocation requirements and
  functional results. A successful short trial is not full qualification.

## Progress

- Step 1 implemented and focused host/physical validation completed. Uploads
  now use a temporary 2 KiB buffer; downloads retain their existing 2 KiB
  chunks. The maximum removed request-body allocation is 96,257 bytes larger
  than the replacement buffer. See [measurements, failures and limits](ESP32C3_WEB_MEMORY_20261013.md).
- Original firmware/settings restored. Steps 2-4 remain pending; no default
  decoder/network pool changes and no claim of full production qualification.

## Fragmentation review: segmented buffers and iterators (2026-10-13)

Recommendation: experiment with fixed-size **1 KiB payload blocks for encoded
input**, while retaining contiguous storage where an existing codec, TLS or
DMA interface requires it. Keep 2 KiB as the control. Splitting every allocation
is not a general replacement for `malloc`: consumers must understand segments.
This section is a design/research update, not an implemented firmware change.

### What the current implementation already provides

- `main/adaptive_input.c` stores separately allocated packets in a descriptor
  table, with pointer, used length, state and next-slot index. The maximum is
  16 data slots plus an independent control slot. The current encoded payload
  size is 2048 bytes (`STREAM_CHUNK_SIZE`); packet headers are additional.
  Only idle blocks can be reclaimed for TLS; WRITING/READY/READING ownership
  prevents freeing data that another task still uses.
- `main/stream_staging.h` already reads a logical byte window across separate
  packet addresses. Four held 2048-byte payloads plus ten lookahead bytes allow
  startup confirmation of a maximum 8191-byte ADTS frame and its next header.
  Its offset-based span lookup scans at most four slots; a persistent cursor
  would be preferable if the number of segments grows substantially.
- `main/native_aac_decoder.c` still assembles a complete ADTS frame in a
  contiguous allocation before calling the native codec. Segmented transport
  does not remove this allocation or change the SDK's input contract.
- `main/decoder_arena.c` reserves one contiguous private region and uses
  `multi_heap` inside it. This isolates decoder allocations from networking,
  but still permits fragmentation inside the region. Free bytes there cannot
  satisfy a TLS request. Its live allocations are not blindly reset at Stop.
- The existing RX-specific TLS reserve provides 17,058 contiguous bytes and
  reuses that region for smaller RX records too. Keep ownership-specific reuse;
  see [the RX reserve implementation](ESP32C3_TLS_RX_RESERVE_20261008.md).

Paths above are relative to `idf/esp32c3-oled-native/`. They describe source
capabilities; whether each experiment is enabled depends on the image config.

### Methods and suitability

| Method | Benefit | Cost or constraint | Priority here |
| --- | --- | --- | --- |
| Allocate large, long-lived objects before small transient objects | Reduces interleaving of incompatible lifetimes | Does not guarantee enough memory or every later allocation | Retain early compact SBR experiment and existing TLS RX reserve |
| Reuse fixed-size blocks from a bounded pool | Eliminates variable-size external fragmentation within that pool; predictable reuse | Unused reserved capacity and last-block slack; the underlying system heap can still fragment | First candidate: encoded input |
| Separate small-object size classes | Avoids spending a 1 KiB block on each tiny object | More pools and a quota decision for each | Consider descriptors/control objects only after measuring demand |
| Region/arena per stream or decoder lifetime | Bulk reuse with little allocation churn | Reset only when decoder, output, callbacks and other tasks have released every reference | Audit existing shared arena rather than add another blanket reserve |
| Stack-like scratch allocation | Cheap temporary reuse with known lifetimes | Free order must really be nested; task stacks themselves need capacity | Codec scratch, with stack high-water and concurrency tests |
| Segmented buffers with span iterators | Large logical data can occupy nonadjacent free blocks | Consumer/API changes; descriptor and boundary overhead | Encoded data and streaming parsers first |
| Split a large codec structure by semantic arrays/channels | Removes the requirement for one large owner allocation | All accessors, resets, copies, assembly and pointer aliases must be converted | Research SBR separately, row/channel sized blocks first |
| Streaming and bounded working windows | Avoids retaining a complete file/request | Requires incremental parsing and correct partial/error handling | Already used for WebUI files; retain it |
| TLSF/coalescing allocator | Efficient reuse and merging of adjacent free blocks | Cannot merge holes separated by live objects or turn scattered blocks into one pointer | Already used by the pinned IDF; not a new fix |
| Relocatable handles/compaction | Can move objects to close holes when all references are mediated | Raw pointers in SDK, DMA and callbacks prevent transparent movement; copy/latency cost | Do not replace the system allocator with a moving allocator |
| Buddy allocator | Simple power-of-two splitting/merging | Rounding can waste substantial RAM; still cannot move live objects | Lower priority than fixed packet pools |

The pinned IDF's `components/heap/multi_heap.c` calls `tlsf_malloc/free/realloc`;
`tlsf.c` merges adjacent free blocks. Allocation placement or heap replacement
cannot transparently satisfy a normal 32 KiB pointer request with scattered
1 KiB pieces. A buffer API with indirection is required.

### Proposed descriptor table and cursor

Keep descriptors in writable internal RAM (normally a static `.bss` array).
A dedicated linker section can organize or audit that table, but does not
create more RAM or defragment payload storage. Addresses allocated at runtime
cannot be kept as an immutable flash table. Never save them across a reboot.

An illustrative 32-bit descriptor is:

```c
struct block_span {
    uint8_t *data;
    uint16_t used;
    uint16_t next; /* pool index; reserved value means end */
};
```

On ESP32-C3 these fields can occupy eight bytes; verify with `_Static_assert`
in an implementation. Real ownership, generation and synchronization state is
additional. Prefer stable pool indices to heap-allocated linked-list nodes.
The cursor holds a current index and offset, exposing `peek_span()` and
`consume(n)`. Process a whole contiguous span in an inner loop and resolve the
next address only at a boundary, rather than performing a pointer lookup for
every byte/sample. A retained span pins its block until explicitly returned.
Small headers crossing a boundary can use bounded scratch storage.

Calculated metadata for **32 KiB logical payload**, assuming the illustrative
eight-byte descriptor only (not measurements of our full queue):

| Payload block | Blocks | Descriptor bytes | Descriptor / payload |
| --- | ---: | ---: | ---: |
| 512 B | 64 | 512 | 1.5625% |
| 1024 B | 32 | 256 | 0.78125% |
| 2048 B | 16 | 128 | 0.390625% |

The pointer array alone for 32 one-KiB blocks would be 128 bytes. Lengths,
ownership, free lists, alignment, allocator headers and unused tail capacity
must also be counted. Smaller chunks lower the individual allocation size;
they do not automatically reduce total payload memory. Reserve/reuse the pool
at startup instead of repeatedly allocating/freeing every arriving packet.

### Boundaries that must stay explicit

1. **Input/parser:** changing 2048 to 1024 without other changes halves the
   four-slot window to 4096 bytes and breaks the maximum ADTS case. Preserve
   at least 8192 payload bytes (eight one-KiB slots), ten-byte lookahead, and
   independent control/drain capacity. Recalculate target/minimum slot counts,
   their 16-slot limit, and the legacy settings conversion using 1600-byte
   budget units. Hold total bytes and prefill duration constant in comparisons.
2. **TLS:** the pinned Mbed TLS `library/ssl_msg.c:mbedtls_ssl_fetch_input`
   uses offsets into `in_buf/in_hdr` and contiguous receive spans. Returning a
   table of blocks from its allocator would break that contract. A scatter/gather
   record-layer rewrite also needs cryptographic/authentication and lifetime
   review. Keep the working contiguous RX reserve as the first choice; never
   expose plaintext before authentication completes or silently restrict valid
   incoming record sizes to avoid allocation.
3. **AAC SBR:** the current compact owner is 32,744 bytes in the tested image.
   It cannot be replaced by 32 pages underneath existing pointer arithmetic.
   Audit every consumer before moving QMF/history arrays out of the owner;
   prefer whole rows/channels and hoist row pointers out of hot loops. Preserve
   the established PCM error bound, complete profile support and speed checks.
4. **DMA:** each submitted DMA span must still have suitable capabilities,
   alignment and lifetime. Hardware descriptor chains are not a generic
   scatter/gather extension to every driver API. Keep the existing four-buffer
   output design for the first input-only experiment.

### Proposed experiments, in order

1. Measure allocation sizes/lifetimes at connection, codec open/reopen, EOF,
   Stop and concurrent WebUI use. Capture matching-capability total/largest
   free blocks **at the failed request**, not just after cleanup. Distinguish
   fragmentation, total shortage and reserved-but-inaccessible memory.
2. Add an opt-in 1024-byte encoded-input configuration; retain a 2048-byte
   control and equal total payload/prefill. Extend existing staging/queue
   ownership tests to eight held blocks before testing the board. Add 512 bytes
   only if the first comparison suggests useful additional benefit.
3. Compare a boot-resident minimum pool with on-demand spare slots. Keep busy
   blocks pinned; exercise pool exhaustion, cancellation, codec changes,
   TLS reclamation and stale-generation rejection without leaks or deadlocks.
4. Measure actual allocation failures, heap recovery, descriptor/padding bytes,
   allocator/queue calls, bytes copied, decoder cycles, startup latency and
   active output errors on the same HE-AACv2, heavy FLAC, MP3, Vorbis and Opus
   workloads. Verify decoded PCM independently where buffer boundaries change.
5. Only if large SBR allocation failures remain, prototype semantic SBR
   suballocations and audit every reader/writer/reset/copy before enabling them.
   A segmented input queue alone does not solve a contiguous SBR allocation.

Acceptance remains functional: no lost format support, playback gaps, crashes,
allocation failures or persistent leaks. A lower absolute free-RAM value alone
does not reject a candidate. These are pending experiments, not measured gains.

### Primary references

- [ESP-IDF 6.1 ESP32-C3 heap allocation](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/system/mem_alloc.html): capability-specific heaps, contiguous regions and largest-block diagnostics.
- [Zephyr memory slabs](https://docs.zephyrproject.org/latest/kernel/memory_management/slabs.html): fixed-size reusable pools as an established embedded design pattern; not a proposed RTOS migration.
- [lwIP packet buffers](https://www.nongnu.org/lwip/2_0_x/group__pbuf.html): chained packet storage; also checked against the pinned local lwIP `src/include/lwip/pbuf.h`.
- [Mbed TLS alternative allocators](https://mbed-tls.readthedocs.io/en/latest/kb/how-to/using-static-memory-instead-of-the-heap/): allocating within a supplied static region; this does not make individual buffer requests scatter/gather.

Local evidence: [early SBR tests and limits](ESP32C3_STREAM_CONFIRMATION_PLAN.md),
[shared decoder arena](ESP32C3_SHARED_DECODER_ARENA_20261012.md), and
[WebUI streaming buffers](ESP32C3_WEB_MEMORY_20261013.md).
