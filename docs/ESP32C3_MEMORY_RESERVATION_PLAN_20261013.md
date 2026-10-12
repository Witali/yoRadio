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

- Plan saved; step 1 in progress. No default decoder/network pool changes.
