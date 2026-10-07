# ESP32-C3 post-Stop heap owner investigation

Date: 2026-10-05. Follow-up to the
[reproduced Vorbis fragmentation](ESP32C3_CUSTOM_DECODER_TERMINAL_20261005.md).

## Question and controlled configuration

The previous MP3 -> Vorbis -> Opus sequence returned total free heap after Stop
but left its largest free block at 94,208 instead of 114,688 bytes. The TCP PCB
pool was already enabled. A successful comparison against the immediately
preceding, already fragmented baseline must not hide loss against the first
baseline. The original failures remain in the previous report.

`CONFIG_YORADIO_HEAP_FRAGMENT_PROBE` observes the current full-rate PC19 AAC
image without changing decoder layouts, format support or buffer sizes. It is
disabled by default. The diagnostic binary is saved under
`firmware/development/esp32c3-heap-fragment-rtc/`; the initial diagnostic is
retained separately in `firmware/development/esp32c3-heap-fragment-probe/`.

## What the probe measures

- After five seconds with no live decoder or PCM workspace, select the actual
  largest free heap range using the IDF heap walker. No allocation address or
  allocator structure offset is hard-coded.
- Use the IDF successful-allocation/free hooks to record pointers, requested
  sizes, increasing allocation/reallocation IDs and a bounded copy of the
  current task name. ISR allocations are labelled `ISR`. No task handle is
  dereferenced later, and no allocated payload is read.
- Track only allocations overlapping that initially free range, at most 128
  live records. Every overflow is counted. Successful in-place reallocations
  update the record; failed reallocations preserve it. Moving reallocations
  retire the old address even when IDF resizes through `multi_heap_realloc`.
- On this single-core C3, free/realloc wrappers hold a recursive critical
  section through the real allocator and post-free hook. This prevents another
  allocation from reusing an address before the old owner is removed. Hooks
  do not allocate or log.
- During subsequent idle periods, match live heap blocks to those records,
  including small allocations. Copy at most 64 rows on the existing decoder
  stack, then print outside all heap locks. Report unknown owners, truncation
  and the walk duration. The analyzer rejects missing/duplicate/malformed rows,
  sequence gaps and incomplete ownership rather than guessing an owner.

This is a set of live snapshots within one region, not a complete all-heap
allocation/free/caller trace. Event counters include successful realloc hooks;
their difference is not a leak calculation. Requested sizes and raw heap-block
sizes are distinct. IDs can change after an in-place resize. Task names are
limited to eleven characters plus the terminator. Call stacks and freed
payloads are not recorded. A task owner narrows the investigation but does not
by itself identify the allocation's responsible function.

The first build adds **3,072 B RTC RAM and 56 B BSS**. The second moves those
counters into RTC as well: **3,128 B RTC RAM, zero extra ordinary DRAM**. RTC
memory is also heap capacity, so this is real diagnostic overhead. IRAM
(43,354 B), initialized DRAM (12,620 B) and the second build's BSS (29,464 B)
match the non-diagnostic image. The RV32 build bounds local snapshot storage at
1,900 B; the host model checks ownership with its different pointer width.
AAC types/features and linked Vorbis repairs remain unchanged. Trace timing
and critical sections make this unsuitable for production CPU qualification.

## Measurements

### Initial trace and extended idle

The complete MP3 -> Vorbis -> Opus sequence uses the same paced 200-second
48 kHz stereo fixtures and 180-second playback windows as the failed baseline.
All three original initial heap-growth gates still fail. All three later
40-second-warmup windows pass their unchanged CPU/heap/progress checks:

| Codec | Later CPU mean / peak | Audio / elapsed time | Max HTTP latency | Largest block after Stop |
| --- | ---: | ---: | ---: | ---: |
| MP3 | 60.48 / 62.3% | 1.00151 | 875 ms | 114688 B |
| Vorbis | 74.54 / 75.9% | 1.00153 | 1484 ms | 114688 B |
| Opus | 80.82 / 81.8% | 1.00165 | 157 ms | 114688 B |

The 14 idle snapshots are complete: no unknown owner, missing row or overflow.
After each Stop the initially free region is again one **115,616-byte raw
free block**, with no live tracked allocation. The allocation-hook high-water
count is 57; the final allocation/free hook counters both read 36,850. The
largest-block API reports 114,688 bytes because this raw block size and the
allocator's allocation-size-class reporting are different measurements.
Maximum snapshot interval is 393 microseconds, not a measured interrupt-latency
bound. The capture does not reproduce the older residual owner.

An additional **130 seconds without HTTP polling**, followed by 12 seconds of
polled idle, keeps the same free region and zero live owners in all 29 captured
snapshots. There is no restart between playback and this observation. Trace
sequences 15–17 fall between the two separate capture sessions; each session is
internally complete. Do not concatenate them and claim a continuous log.

### Repeat with unchanged ordinary DRAM

The repeat moves all probe counters to RTC RAM. ELF comparison confirms the
same addresses and sizes for ordinary DRAM data/BSS and IRAM as the control.
MP3 and Vorbis again play for 180 seconds each, without rebooting between them:

| Codec | Later CPU mean / peak | Audio / elapsed time | Max HTTP latency | Largest block after Stop |
| --- | ---: | ---: | ---: | ---: |
| MP3 | 60.96 / 62.2% | 1.00169 | 125 ms | 114688 B |
| Vorbis | 74.39 / 75.5% | 1.00153 | 140 ms | 114688 B |

Both original initial heap-growth gates fail. The supplementary later MP3
window still fails heap-growth checking; the later Vorbis window and all idle
recovery gates pass. Nine complete snapshots again find no live
owner and one raw free block of 115,616 B. Peak live allocations are 53,
allocation/free hook counters finish at 24,883 each, and the maximum snapshot
interval is 386 microseconds. These results do not identify or fix the owner
of the earlier 20 KiB largest-block loss. Vorbis plan step 4 remains open.

Three physical WebUI OTA transitions (initial probe, RTC probe, restored
control) pass image and settings/Wi-Fi/playlist identity checks. The first
transition's serial capture ends with an incomplete line: its separately
replayed serial-health gate fails. The other two serial-health checks pass.
This capture limitation does not invalidate the independent image/settings
readback, but prevents a complete clean-log claim for the first OTA. The final
board check confirms the non-probe, non-deep-sleep image
`6eea8a8f2f9039999f6873fdd7d0ab48e2c9d79179f208111a536a6fd91c99ab`
and the restored AAC 44.1 kHz stereo station playing.

## Reproduction and retained checks

```powershell
python tests/test-heap-fragment-probe.py
python tests/test-heap-fragment-log.py
python tests/test-heap-idle.py
python tests/test-heap-fragment-evidence.py
python tools/esp32c3_tests/heap_fragment.py PATH_TO_RUN/performance.json --output PATH_TO_RUN/owners.json
```

The native test compiles the actual probe with allocator/task doubles under
ASan/UBSan, covering activation, range selection, task-name copying, ISR,
realloc failure/in-place/moving/zero-size cases, free/reuse, overflow, unknown
owners, snapshot bounds and logging outside locks. The parser tests reject
damaged or incomplete records. The linked build verifier checks the allocation,
free, realloc and decoder-task hook call sites in the actual ELF.

For the physical run use the shared 200-second high-bitrate fixtures and
`diagnostic.py run --suite load --load-seconds 180 --load-idle-recovery` with
MP3, Vorbis and Opus in that order, the exact diagnostic `sdkconfig`, and
`--leave-stopped` for subsequent idle observation. Preserve original load gates
even though the traced image is diagnostic. Return to the non-diagnostic image
through WebUI OTA after collecting evidence; verify image and settings identity.

For already-stopped passive observation use
`heap_idle.py --board http://BOARD_IP --serial-port COM_PORT --quiet-seconds 130 --output OUTPUT_DIR`.
Its host test verifies that no HTTP request is sent during the quiet window.
The [retained evidence manifest](../tests/results/esp32c3-heap-fragment-20261005/manifest.json)
covers raw filtered logs, reports, both build verifications, exact runner/source
snapshots, sanitizer checks and summaries. Frozen build sources precede the
final Kconfig requirement for a flash-resident allocator; both tested configs
already enable that requirement. That constraint adds no runtime code.

## Opus delivery follow-up

In the previous uninstrumented failure, multiple Opus windows show only
1.6–3.5 seconds of decoded audio per five seconds, while decoder cost remains
approximately half the decoded audio duration. CPU usage decreases and sampled
TCP receive windows are fully available. This is consistent with insufficient
input delivery, not proof of its cause. The new optional shared-server
`--delivery-stats` records host socket-write timing and pacing delay without
changing bytes or the acceptance gates. Host writes are not acknowledgements;
use matching board observations to distinguish sender, network and consumer.

After restoring the control, a separate 180-second Opus run records 11,649,024
bytes in 180 complete sender windows, without dropped windows. Its longest
completed socket write takes 110 ms. The maximum cumulative pacing lateness is
1.920 s. With the server deliberately pacing at 1.02 times the average bitrate,
normal receiver backpressure can accumulate lateness; that value alone is not
an audio underrun or a network-stall measurement.

The later board windows report mean/peak CPU of 79.72/80.5%, decoded audio/time
of 1.00170, and maximum HTTP latency of 140 ms (minimum RSSI -74 dBm). Stop
restores 147,872 B free heap, 114,688 B largest block and 17 tasks. Nevertheless,
**both original and supplementary CPU/heap acceptance remain FAIL**: one CPU
line is damaged, changing from `heap` into the tail of another telemetry
message. The required `heap` and `largest` fields are absent. No missing fields
are reconstructed or discarded to turn the run into PASS. The retained raw
line and replay test preserve this evidence gap. The older Opus slowdown did
not recur in the available complete decoder windows, but this run is not a
complete CPU/memory qualification or an acoustic continuity test.
