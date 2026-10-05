# ESP32-C3 receive-buffer ownership during long playback

Date: 2026-10-05. Follow-up to the [DMA prefill experiment](ESP32C3_OUTPUT_DMA_20261005.md)
and step 4 of the [Vorbis plan](ESP32C3_VORBIS_REPAIR_PLAN.md).

## Result and scope

The initial drop in free heap includes retained Wi-Fi RX packet allocations.
This is now measured through public netif ownership transfers and live heap
ranges, rather than inferred only from repeated allocation sizes. Vorbis
stabilizes during the subsequent 120-second window and recovers the original
114,688-byte largest free block after Stop in these runs.

The original 40-second progressive-heap-loss FAIL remains in each report.
Acceptance thresholds have not changed. This does not resolve the earlier
post-stop fragmentation failure or qualify every codec/stream combination.
The owner of the allocation that split the idle heap in that older run remains
unknown. The MP3 -> Vorbis -> Opus sequence and complete allocation lifecycle
tracing remain pending.

## Instrumentation

`CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=y` adds a 32-entry table to the existing
PC19, full-rate AAC/SBR/PS, four-DMA-block image. The option defaults off and is
restricted to the physical C3. The saved diagnostic image uses no deep sleep.

- Wrap `esp_pbuf_allocate` after successful allocation and
  `esp_netif_free_rx_buffer` before freeing. Call the real functions unchanged.
- Record an increasing lifetime ID, opaque L2 handle, payload pointer and
  public pbuf pointer. Never read packet contents or interpret private driver
  fields. No hard-coded structure offsets or allocation addresses are used.
- Every five seconds, on the existing decoder task between decode calls,
  locate those pointers inside allocated heap ranges. Deduplicate shared
  allocations. Include small metadata allocations as well as packet storage.
- Hold a short critical section across the ownership snapshot and heap walk on
  the single-core C3; emit logs only after leaving it. Allocation wrappers take
  this lock only after allocation returns; free wrappers release it before
  calling the underlying free. The heap-walk callback does not allocate/log.
- Report table overflow, ambiguous handle reuse, unmatched frees and missing
  ranges. Reject incomplete sequences, malformed rows and inconsistent counts
  in the host analyzer; never silently drop a damaged snapshot.

Linked BSS grows from 29,464 to **30,016 bytes: +552 bytes**. IRAM stays at
43,354 bytes. The RV32 compiler verifies the local snapshot is at most 1,100
bytes. The host sanitizer model uses 64-bit pointers, so only the real target
build checks that particular bound. AAC allocation sizes and features match
the non-diagnostic prefill image.

These are snapshots of live netif RX owners and cumulative counters, not a
trace of all allocations/frees. Short-lived packets can occur between samples.
Counts include WebUI/control traffic. TCP copies, unrelated heap owners and
allocator headers are outside the directly measured RX payload capacity.
This diagnostic changes timing and must not serve as production CPU/IRQ
qualification.

## Hardware procedure and results

Each load run uses a synthetic 200-second 48 kHz stereo fixture: 40 seconds
initial playback plus 120 seconds uninterrupted settled playback, with 12-second
idle checks before/after. The same HTTP connection stays open between phases;
the server sends at 1.02 times average encoded bitrate. WebUI is polled during
playback. After Stop, compare total free heap, largest block and task count.

All five runs retain the initial progressive-heap-loss FAIL. The CPU figures
below describe the settled window; the trace-heavy rows are diagnostic results.

| Run | Settled CPU mean / peak | Audio / wall time | Settled acceptance | Idle free-heap median before -> after | Largest block after Stop | RX ownership capture |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Vorbis, prefill image without RX tracing | 73.55 / 74.7% | 1.00154 | PASS | 147788 -> 147782 B | 114688 B | Not enabled |
| Vorbis, first diagnostic run | 73.45 / 74.8% | 1.00155 | PASS | 147280 -> 147232 B | 114688 B | Rejected: truncated line |
| Vorbis, chunked reader | 73.80 / 75.0% | 1.00152 | PASS | 147244 -> 147222 B | 114688 B | Complete |
| MP3 320 kb/s, chunked reader | 60.18 / 61.4% | 1.00172 | PASS | 147310 -> 147344 B | 114688 B | Rejected: three missing block rows |
| Opus, chunked reader | 80.07 / 81.0% | 1.00172 | **FAIL: WebUI 3078 ms** | 147430 -> 147468 B | 114688 B | Complete |

The Opus CPU/heap subchecks pass when replayed independently, but the original
load test fails its 2-second HTTP-response limit. Do not relabel it as PASS.
The cause of that response delay has not been established. Task count returns
to 17 in all five runs. Small free-heap variations are not proof that every
non-RX allocation has identical lifetime/address.

For the complete Vorbis capture, initial snapshots grow from zero to nine live
RX packets; settled snapshots contain 8–10. Their allocated payload capacity
peaks at 17,644 bytes. All three post-stop snapshots contain zero live RX
owners, with allocations equal to frees. No table overflow, unmatched free or
missing heap range was observed in that run.

Opus also has 8–10 live RX owners during settled playback and zero in all three
post-stop snapshots; its maximum allocated payload capacity is 17,912 bytes.
The maximum measured owner-snapshot/heap-walk interval is 977 microseconds for
Vorbis and 1,656 microseconds for Opus. This interval includes entry/exit and
possible scheduling around the critical section; it is not a measured worst-case
interrupt latency. The smallest logged decoder stack margins are retained in
the raw performance logs, not inferred from the host test.

Typical individual allocations are 1,728 bytes of packet storage and 28 bytes
of pbuf metadata. Some allocated ranges are larger (1,792-byte payloads and
32/36/40-byte metadata); the analyzer uses measured sizes, not fixed estimates.
With the pinned C3 TLSF allocator and poisoning/task tracking disabled, each
unique allocation also consumes a four-byte size header. Thus a typical pair
accounts for **1,728 + 28 + 2 × 4 = 1,764 bytes** of free-heap change. This
explains the observed step size; it does not attribute every byte of total
heap movement. The stored SDK sources show `block_header_overhead`,
`tlsf_alloc_overhead()` and `multi_heap_malloc_impl`/`multi_heap_free_impl`.

The first diagnostic Vorbis run had a merged/truncated USB line. Its playback
and recovery results remain saved, but its **ownership capture is rejected**.
The host reader now drains serial data in chunks instead of byte-at-a-time
`readline()`, and preserves incomplete lines across read timeouts. Unit tests
cover timeout splits, 1,000-line bursts, filtering, overlong lines, incomplete
termination and I/O errors. The repeated Vorbis run used the same firmware and
produced a complete ownership capture. This does not guarantee USB can never
lose data: three RX block rows were still missing from one MP3 snapshot, and
that ownership capture is rejected too. Sequence/count checks remain mandatory.

## Evidence and reproduction

The [retained evidence](../tests/results/esp32c3-rx-ownership-20261005/manifest.json)
includes raw filtered reports (including failures), summaries, source snapshots,
SDK allocator sources, fixture identities, linked call disassembly and host
sanitizer results. Runtime test dependencies are preserved by their reported
SHA-256; unrelated modules in the runner's broad source inventory are not copied.
No packet data, Wi-Fi credentials or playlist contents are retained.

Build the same prefill configuration with
`CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=y`; use the Vorbis build verifier to check
the five linked RX wrapper/call sites. The diagnostic artifact is saved in
`firmware/development/esp32c3-rx-owner-diagnostic/`.

```powershell
python tests/test-rx-buffer-diagnostic.py
python tests/test-rx-ownership.py
python tests/test-serial-telemetry.py
python tests/test-rx-ownership-evidence.py

python tools/esp32c3_tests/diagnostic.py pool_settle --board http://BOARD_IP --host HOST_IP --serial-port COM_PORT --fixture-manifest PATH_TO_STRESS_MANIFEST --case stress-vorbis-48000-2ch-16bit-200s --initial-seconds 40 --settled-seconds 120 --output .build/rx-recheck
python tools/esp32c3_tests/summarize_rx_ownership.py .build/rx-recheck --output .build/rx-recheck/summary.json
```

The pool-settle command intentionally exits nonzero when its original initial
heap gate fails, even when the settled phase and recovery pass. Inspect each
case. Fixture generation requires the recorded FFmpeg version/options and the
matching byte hashes. The native host test requires WSL GCC/ASan/UBSan on Windows.

After the diagnostic runs, OTA reinstalls the non-diagnostic
`esp32c3-output-dma-prefill` image (ELF SHA-256 beginning `323799dc5e78`). The
saved OTA report checks Wi-Fi settings, playlist and other settings against
their in-memory snapshots. The final board record checks image identity and
active saved-station playback. No NVS/SPIFFS erase or serial flash is involved.

Next: obtain a complete MP3 ownership capture; reproduce the earlier codec
sequence that left the largest idle block fragmented; trace the actual residual
owner; investigate the Opus WebUI delay on the non-diagnostic image. Keep
network startup filling, post-stop fragmentation and output continuity as
separate acceptance checks.
